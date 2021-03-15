from typing import Type
from fastapi.exceptions import RequestValidationError
from .schemas import AppException, RFC7807


def map_message_from_message_type(message_type):
    if message_type == "success":
        raise NotImplementedError()
    elif issubclass(message_type, Exception):
        return map_message_from_exception_type(message_type)
    else:
        raise Exception()


def map_message_from_success_type(success_cls):
    return None


def map_message_from_exception_type(exc: Exception) -> AppException:
    exc_cls = exc.__class__
    if not issubclass(exc_cls, Exception):
        return None

    # 継承の関係があるため、子クラスを優先に並べること
    if issubclass(exc_cls, RequestValidationError):
        result = AppException(type=exc, code=422, title="処理要求時に検証エラーが発生しました。", get_errors=lambda self: self.errors())
    elif issubclass(exc_cls, ValueError):
        result = AppException(type=exc, code=422, title="処理要求時に検証エラーが発生しました。")
    elif issubclass(exc_cls, SystemError):
        result = AppException(type=exc, code=500, title="処理要求時に想定外のシステムエラーが発生しました。")
    else:
        result = None

    if not result:
        result = AppException(type=exc, code=500, title="処理要求時に想定外のシステムエラーが発生しました。")

    return RFC7807(result)

