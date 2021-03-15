from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from libs.pydantic import BaseModel as Model
from pandemic import Unpack

if TYPE_CHECKING:
    from dataclasses import dataclass as intellisense
else:

    def intellisense(cls):
        """
        dataclassに擬態する。vscodeの場合pydanticの補完が効かないため。
        なお、sqlalchemyのモデルに適用しても効果がない。なぜだ。。
        """
        return cls


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

    # argsは追加しないこと。fastapiで誤作動が生じることがある
    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # type: ignore
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
    warning: str = ""


class EtlJobResult(BaseModel):
    name: str
    deleted: int = 0
    inserted: int = 0
    errors: List[Any] = []
    error_summary: str = ""
    warning: str = ""
