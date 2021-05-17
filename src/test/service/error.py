from fastapi import HTTPException


class HttpTimeoutException(HTTPException):
    status_code = 504


class HttpAllResponsesFailedException(HTTPException):
    status_code = 512
    detail = 'All responses failed'

    def __init__(self):
        super(HttpAllResponsesFailedException, self).__init__(
            status_code=HttpAllResponsesFailedException.status_code,
            detail=HttpAllResponsesFailedException.detail)
