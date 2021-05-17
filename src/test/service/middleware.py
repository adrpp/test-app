from typing import Any
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from test.service.config import REQUEST_ID_HEADER


class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to store Request ID headers value inside request's state object.

    Use this class as a first argument to `add_middleware` func:

    .. code-block:: python

        app = FastAPI()

        @app.on_event('startup')
        async def startup():
            app.add_middleware(RequestIdMiddleware)
    """

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        """
        Get header from request and save it in request's state for future use.
        :param request: current Request instance
        :param call_next: next callable in list
        :return: response
        """
        request_id = request.headers.get(REQUEST_ID_HEADER)
        if not request_id:
            request_id = uuid4()
        request.state.request_id = request_id
        response = await call_next(request)
        return response
