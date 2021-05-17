"""
copied from
https://github.com/raphaelauv/fastAPI-aiohttp-example/blob/master/src/fastAPI_aiohttp/fastAPI.py
"""

import aiohttp
import asyncio
import logging

from socket import AF_INET
from typing import Optional, Any

from fastapi.exceptions import HTTPException

from test.service.config import SIZE_POOL_AIOHTTP

logger = logging.getLogger('test.service')


class SingletonAiohttp:
    sem: Optional[asyncio.Semaphore] = None
    aiohttp_client: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None:
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(family=AF_INET, limit_per_host=SIZE_POOL_AIOHTTP)
            cls.aiohttp_client = aiohttp.ClientSession(timeout=timeout, connector=connector)

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def query_url(cls, url: str) -> Any:
        client = cls.get_aiohttp_client()

        try:
            async with client.get(url) as response:
                if response.status != 200:
                    return HTTPException(status_code=response.status, detail=str(await response.text()))

                json_result = await response.json()
        except (asyncio.exceptions.TimeoutError, asyncio.exceptions.CancelledError) as e:
            return e
        except Exception as e:
            raise e

        return json_result


async def start_up_asyncio_client() -> None:
    logger.info("start up asyncio client")
    SingletonAiohttp.get_aiohttp_client()


async def close_asyncio_client() -> None:
    logger.info("close asyncio client")
    await SingletonAiohttp.close_aiohttp_client()
