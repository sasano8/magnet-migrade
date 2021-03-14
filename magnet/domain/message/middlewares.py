from fastapi import HTTPException, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from magnet import asgi_app as app

from . import crud
from .errors import ErrorBase


def convert_to_json_response_from_error(exc):
    err = crud.map_message_from_exception_type(exc)
    if err is None:
        raise

    dic = err.dict()
    content = jsonable_encoder(dic)

    return JSONResponse(status_code=err.code, content=content)


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(request, exc):
    res = convert_to_json_response_from_error(exc)
    if res is None:
        raise

    return res


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response = await call_next(request)
        except Exception as exc:
            res = convert_to_json_response_from_error(exc)
            if res is None:
                raise

            return res
        else:
            return response
