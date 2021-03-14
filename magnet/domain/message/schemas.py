from typing import Any, Callable, Dict, List, Type, Union

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from pydantic import Field
from pydantic.error_wrappers import ErrorWrapper

from ...commons import BaseModel


class SuccessMessage(BaseModel):
    pass


class ErrorMessage(Exception):
    pass


class AppException(BaseModel):
    code: int = 500
    type: Exception
    title: str = ""
    detail: str = ""

    get_errors: Any

    class Config:
        arbitrary_types_allowed = True

    def to_err_dict(self, exc):
        dic = super().dict()
        dic["type"] = self.type.__name__
        # dic["detail"] = str(exc)
        return dic

    def append_by_code(
        self, code: int, loc=None, values: dict = {}
    ) -> "ValidationError":
        from .errors_message import messages_jp

        e_info = messages_jp[code]
        self.append(exc_type=e_info["exc"], msg=e_info["msg"], loc=loc, values=values)
        return self

    def append(
        self, msg: str, loc=None, exc_type=ValueError, values: dict = {}
    ) -> "ValidationError":
        # if len(kwargs) is not undefined:
        msg = msg.format(**values)

        e = ErrorWrapper(exc_type(msg), loc)
        self.raw_errors.append(e)
        return self


from pydantic import BaseModel


class LocTypes(BaseModel):
    path: str
    query: str
    body: str


class LocInfo(BaseModel):
    loc: List[str]
    msg: str
    type: str


class RFC7807(BaseModel):
    code: int = Field(description="サーバによって生成されたHTTPステータスコード")
    type: str = Field(description="エラーの詳細ドキュメントへのURL")
    title: str = Field(description="人間が読むためのサマリー")
    detail: str = Field("", description="人間が読むことのできる説明文")
    instance: str = Field("about:blank", description="問題発生箇所の参照URI")

    errors: List = Field(None, description="アプリ固有のURIスキーマ")

    def __init__(self, exc: AppException):
        # exc = exc.type.errors()
        errors = []

        # TODO: content-type application/problem+json
        #       content-language en

        super().__init__(
            code=exc.code,
            type=exc.type.__class__.__name__,
            title=exc.title,
            detail=str(exc.type),
            instance=exc.instance,
            errors=errors,
        )

    class Config:
        schema_extra = {
            "examples": [
                {
                    "code": 200,
                    "type": "value error",
                    "title": "",
                    "instance": [
                        {
                            "loc": ["body", "name"],
                            "msg": "invalid name",
                            "type": "type.error",
                        }
                    ],
                }
            ]
        }
