from fastapi import status
from fastapi.exceptions import HTTPException, RequestValidationError
from pydantic import PydanticValueError
from pydantic.error_wrappers import ErrorWrapper

from .error_messages import ErrorCode, messages_en, messages_jp


class Undefined:
    pass


undefined = Undefined()


# class ValueErrorDetail(PydanticValueError):
#     code = 'value_error'
#     msg_template = 'value is not "bar", got "{value}"'


class RFC7807:
    status: str = "サーバによって生成されたHTTPステータスコード"
    type: str = "エラーの詳細ドキュメントへのURL"
    title: str = "人間が読むためのサマリー"
    detail: str = "人間が読むことのできる説明文"
    instance: str = "問題発生箇所の参照URI"

    # アプリケーション固有フィールド
    errors: list

    def __init__(self, status, type, title, detail, instance, errors):
        pass


class ErrorBase(Exception):
    pass


class SystemError(ErrorBase):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        errors: list = [],
    ):
        pass


class ApiError(ErrorBase):
    def __init__(
        self, status_code: int = status.HTTP_400_BAD_REQUEST, errors: list = []
    ):
        pass


class ValidationError(RequestValidationError):
    def __init__(self):
        super().__init__([])
        self.raw_errors = []

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

    @staticmethod
    def create_sample_json_error():
        import json

        s = '{"name": undefined}'

        # fastapiはこのようにValidation Errorを組み立てている
        try:
            json.loads(s)

        except json.JSONDecodeError as e:
            return RequestValidationError(
                [ErrorWrapper(e, ("body", e.pos))], body=e.doc
            )

    @staticmethod
    def create_sample_pydantic_error():
        from pydantic import BaseModel, validator

        class Sample(BaseModel):
            name: str

            @validator("name")
            def valid_name(cls, v, values, **kwargs):
                raise ValueError("invalid name")

        try:
            Sample()

        except Exception as e:
            return RequestValidationError(
                [ErrorWrapper(e, ("body", e.pos))], body=e.doc
            )
