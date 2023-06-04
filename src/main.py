from fastapi import FastAPI, Request
from fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi.responses import JSONResponse

from src.buttons.router import router as buttons_router
from src.auth.router import router as auth_router
from src.openapi import custom_openapi
from .config import FastApiSettings

settings = FastApiSettings()

app = FastAPI(
    **settings.dict()
)

app.openapi = custom_openapi(app)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(
        status_code=exc.status_code,
        content={'status': 'Failed authorization',
                 'data': '',
                 'detail': exc.message}
    )


app.include_router(auth_router)

app.include_router(buttons_router)

