from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from libs.pydantic import BaseModel as Model
from pandemic import Unpack

from .utils.objects import Service

if TYPE_CHECKING:
    pass
else:
    origin_dataclass = dataclass
    from pydantic import BaseModel as M

    def dataclass(cls):
        """dataclasses.dataclassと同様に振る舞う。ただし、pydantic.BaseModelの場合は何もしない。これは、VSCodeで初期化時の補完を働かせるためのハックです。"""
        if issubclass(cls, M):
            return cls
        else:
            return origin_dataclass(cls)


class BaseModel(Model):
    class Config:
        allow_population_by_field_name = True  # エイリアス名でデータを入力できる
        allow_mutation = True  # イミュータブルだと利便性が悪いため、ミュータブルとする
        extra = "forbid"  # 追加属性を禁止
        validate_assignment = True  # 属性へ値代入時に再検証を行う
        # underscore_attrs_are_private = True  先頭アンダースコア一つはプライベートとして扱う

        # dateでもdatetime互換の形式で出力したいが、pydanticがisoformatをdateと認識してくれないため、復元時にエラーとなってしまう
        # datetimeオブジェクトをdateフィールドに設定する分には、dateに変換してくれる
        # 問題となるのは、dateフィールドとしてjsonにシリアライズ、dateフィールドをdatetimeに変更した際
        # json_encoders = {
        #     datetime.date: lambda v: datetime.datetime(year=v.year, month=v.month, day=v.day).isoformat(),
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # type: ignore
        self.__post_init__()

    def __post_init__(self):
        ...


class PagenationQuery(BaseModel, Unpack):
    skip: int = 0
    limit: int = 100
    _kwargs: Dict[Literal["aa", "b", "c"], str] = {}

    class Config:
        fields = {
            "skip": "from",
        }


class BulkResult(BaseModel):
    deleted: int = 0
    inserted: int = 0
    errors: List[Any] = []
    error_summary: str = ""


class TaskResult(BaseModel):
    name: str
    deleted: int = 0
    inserted: int = 0
    errors: List[Any] = []
    error_summary: str = ""
