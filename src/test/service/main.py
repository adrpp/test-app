
import asyncio
import logging.config

from fastapi import FastAPI, Request
from logging import getLogger
from typing import List, Union

from test.service.config import CLIENT_URL, NUMBER_OF_TASKS, LOGGER_CONF
from test.service.error import HttpAllResponsesFailedException
from test.service.middleware import RequestIdMiddleware
from test.service.singleton_aiohttp import start_up_asyncio_client, close_asyncio_client, SingletonAiohttp

logging.config.dictConfig(LOGGER_CONF)
logger = getLogger('test.service')

app = FastAPI(
    on_startup=[start_up_asyncio_client],
    on_shutdown=[close_asyncio_client],
    debug=True)
app.add_middleware(RequestIdMiddleware)


@app.get("/api/all")
async def api_all(request: Request, timeout: int):
    results = await _execute_tasks(NUMBER_OF_TASKS, timeout)

    successful_responses = _filter_successful_responses(results, request.state.request_id)
    if successful_responses:
        return successful_responses
    else:
        raise HttpAllResponsesFailedException()


@app.get("/api/first")
async def api_first(request: Request, timeout: int):
    results = await _execute_tasks(NUMBER_OF_TASKS, timeout, asyncio.FIRST_COMPLETED)

    successful_responses = _filter_successful_responses(results, request.state.request_id)
    if successful_responses:
        return successful_responses[0]
    else:
        raise HttpAllResponsesFailedException()


@app.get("/api/within-timeout")
async def api_within_timeout(request: Request, timeout: int):
    results = await _execute_tasks(NUMBER_OF_TASKS, timeout, asyncio.FIRST_COMPLETED)

    successful_responses = _filter_successful_responses(results, request.state.request_id)
    if successful_responses:
        return successful_responses
    else:
        return list()


@app.get("/api/smart")
async def api_smart(request: Request, timeout: int):
    request_id = request.state.request_id
    first_timeout = min(timeout, 300)
    remaining_timeout = max(timeout - first_timeout, 0)

    first_task = asyncio.create_task(SingletonAiohttp.query_url(CLIENT_URL))
    done, pending = await asyncio.wait([first_task], timeout=first_timeout/1000)
    if done:
        try:
            first_result = first_task.result()
            if isinstance(first_result, Exception):
                raise first_result
        except Exception as e:
            logger.debug(f'first request finished with errors: "{repr(e)}" {request_id}')
        else:
            logger.debug(f'first request finished with success: "{first_result}" {request_id}')
            return first_result

    elif not done and remaining_timeout > 0:
        tasks = [first_task]
        tasks.extend(_generate_async_tasks(2))
        done, pending = await asyncio.wait(tasks, timeout=(remaining_timeout / 1000), return_when=asyncio.FIRST_COMPLETED)
        if done:
            for done_task in done:
                try:
                    first_successful_result = done_task.result()
                    if isinstance(first_successful_result, Exception):
                        raise first_successful_result
                except Exception as e:
                    logger.debug(f'request finished with errors: "{repr(e)}" {request_id}')
                    continue
                else:
                    logger.debug(f'request finished with success: "{first_successful_result}" {request_id}')
                    return first_successful_result

    logger.debug(f'no request successful or finished {request_id}')
    _cancel_pending_tasks(pending)
    raise HttpAllResponsesFailedException()


async def _execute_tasks(
        no_of_tasks: int,
        timeout_in_milisecs: int,
        return_when: Union[None, asyncio.FIRST_COMPLETED] = None,
        cancel_pending: bool = True):

    timeout_in_seconds = (timeout_in_milisecs - 50) / 1000
    tasks = _generate_async_tasks(no_of_tasks)
    if return_when:
        done, pending = await asyncio.wait(tasks, timeout=timeout_in_seconds, return_when=return_when)
    else:
        done, pending = await asyncio.wait(tasks, timeout=timeout_in_seconds)

    if cancel_pending:
        _cancel_pending_tasks(pending)
    results = _results_from_tasks(tasks)
    return results


def _generate_async_tasks(no_of_tasks: int) -> List[asyncio.Task]:
    tasks = list()
    for no_of_req in range(no_of_tasks):
        tasks.append(asyncio.create_task(SingletonAiohttp.query_url(CLIENT_URL)))
    return tasks


def _cancel_pending_tasks(pending_tasks):
    for task_to_cancel in pending_tasks:
        task_to_cancel.cancel()


def _results_from_tasks(tasks: List[asyncio.Task]) -> List[Union[dict, Exception]]:
    results = list()
    for task in tasks:
        try:
            result = task.result()
        except Exception as e:
            results.append(e)
        else:
            results.append(result)
    return results


def _filter_successful_responses(results: List[Union[dict, str, Exception]], request_id: str) -> List[Union[dict, str]]:
    successful_responses = [resp for resp in results if not isinstance(resp, (Exception, asyncio.exceptions.CancelledError))]
    logger.debug(f'successful responses {len(successful_responses)} out of {len(results)} responses in total {request_id}')
    return successful_responses
