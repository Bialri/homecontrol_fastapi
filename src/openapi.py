from typing import Any, Callable, Dict
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def custom_openapi(app: FastAPI) -> Callable[[], Dict[str, Any]]:

    def openapi_generator() -> Dict[str, Any]:
        if app.openapi_schema:
            return app.openapi_schema
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        openapi_schema["components"]["securitySchemes"] = {"bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }}

        openapi_schema["security"] = [{"bearerAuth": []}]

        app.openapi_schema = openapi_schema
        return app.openapi_schema
    return openapi_generator
