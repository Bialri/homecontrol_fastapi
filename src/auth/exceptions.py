from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi_jwt_auth.exceptions import AuthJWTException


def authjwt_exception_handler(exc: AuthJWTException,
                              response_status: Response):
    response_status.status_code = exc.status_code
    return JSONResponse(
        content={'status': 'Failed authorization',
                 'data': '',
                 "detail": exc.message})
