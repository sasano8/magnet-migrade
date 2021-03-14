from __future__ import annotations

from typing import Any, Iterable, Type, TypeVar, Union

import pytz
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel as PydanticModel
from pydantic import BaseSettings as PydanticSettings

from .utils import generate_funnel

alias_all = {
    "False_": "False",
    "None_": "None",
    "True_": "True",
    "and_": "and",
    "as_": "as",
    "assert_": "assert",
    "break_": "break",
    "class_": "class",
    "continue_": "continue",
    "def_": "def",
    "del_": "del",
    "elif_": "elif",
    "else_": "else",
    "except_": "except",
    "finally_": "finally",
    "for_": "for",
    "from_": "from",
    "global_": "global",
    "if_": "if",
    "import_": "import",
    "in_": "in",
    "is_": "is",
    "lambda_": "lamdba",
    "nonlocal_": "nonlocal",
    "not_": "not",
    "or_": "or",
    "pass_": "pass",
    "raise_": "raise",
    "return_": "return",
    "try_": "try",
    "while_": "while",
    "with_": "with",
    "yield_": "yield",
}

alias_min = {
    "from_": "from",
    "class_": "class",
    "return_": "return",
    "global_": "global",
}

# Model = TypeVar("Model", bound="BaseModel")
Model = TypeVar("Model", bound=PydanticModel)
# from pydantic import BaseModel as PydanticModel
# from pydantic import BaseSettings as PydanticSettings
# Model = Type[Union[PydanticModel, PydanticModel]]


class BaseConfig:
    fields = alias_min
    allow_population_by_field_name = True  # インスタンス生成時のパラメータを、# フィールド名・エイリアスの両対応とする
    validate_assignment = True  # 属性更新時の検証を有効にする


# noinspection PyTypeChecker
# class BaseModel(PydanticModel):
#     class Config:
#         validate_assignment = True  # 属性更新時の検証を有効にする


class MixinModel:
    @classmethod
    def from_orm_query(cls: Type[Model], query: Iterable[Any]) -> Iterable[Model]:
        for item in query:
            yield cls.from_orm(item)

    @classmethod
    def from_orm_query_as_dict(
        cls: Type[Model], query: Iterable[Any]
    ) -> Iterable[dict]:
        for item in cls.from_orm_query(query):
            yield item.dict()

    @classmethod
    def new_type(
        cls: Type[Model], prefix: str = "", name: str = ..., suffix: str = ""
    ) -> Type[Model]:
        if name == ...:
            name = cls.__name__
        else:
            name = name

        return type(prefix + name + suffix, (cls,), {})

    # obj.prefab(fields={
    #   "name"=..., # required
    #   "name"=None, # optional
    #   "name"=1, # default
    #   "name"=del, # exclude
    # })

    @classmethod
    def prefab(
        cls: Type[Model],
        prefix: str = "",
        name: str = ...,  # TODO: test
        suffix: str = "",
        exclude: set = set(),
        requires: set = set(),
        optionals: Union[set, dict] = {},
    ) -> Type[Model]:
        """
        出力するフィールドを制限し、指定されたフィールドの必須・オプション属性を更新した新しいスキーマクラスを生成する。
        requires = None: 必須属性を引き継ぐ(デフォルト)(#TODO: 仕様が異なっているので正すこと)
        requires = ...: 全てのフィールドを必須にする
        requires = {a,b,c}: 指定したフィールドを必須にする
        optionals = None : フィールドのオプション属性を引き継ぐ（デフォルト）(#TODO: 仕様が異なっているので正すこと)
        optionals = ... : 全てのフィールドをオプションにする。
        optionals = ["field1", "field2"] : 指定したフィールドをオプションにする
        optionals = {"field1": "val", "field2": "val"}: 指定したフィールドに指定したデフォルト値を設定する(#TODO: 未実装)
        exclude = None: フィールドを除外しない（デフォルト）(#TODO: 仕様が異なっているので正すこと)
        exclude = ...: 全てのフィールドを除外する
        exclude = {a,b,c}: 指定したフィールドを除外する
        """
        new_type = cls.new_type(prefix=prefix, name=name, suffix=suffix)

        if exclude is ...:
            exclude = {key for key in new_type.__fields__.keys()}

        # 指定されたフィールドを除外する
        for item in exclude:
            del new_type.__fields__[item]
            # if item in new_type.__fields_set__:  # エイリアスなど拡張属性が格納されてるっぽい
            #     del new_type.__fields_set__
            # new_type.__field_defaults__.pop(item, None)
            # new_type.__validators__

        if requires is ... and optionals is ...:
            raise KeyError(
                "Only one of required and optionals can be specified as all(...)"
            )

        if requires is ...:
            requires = {
                key for key in new_type.__fields__.keys()
            }  # excludeフィールドは除外されます
        if len(requires) == 0:
            requires = set()
        else:
            requires = {key for key in requires}

        if optionals is ...:
            # 必須指定された以外のフィールドをオプションとする
            optionals = {
                key for key in new_type.__fields__.keys() if key not in requires
            }  # excludeフィールドは除外されます
        if len(optionals) == 0:
            optionals = {}
        else:
            optionals = {key: None for key in optionals}

        # 指定されたフィールドを必須にする
        for key in requires:
            new_type.__fields__[key].required = True

        # 指定されたフィールドをオプションにする
        for key in optionals.keys():
            if key in requires:
                raise KeyError(f"conflict required and optional field: {key}")
            new_type.__fields__[key].required = False

        return new_type

    @classmethod
    def as_func(cls):
        """
        モデル属性を関数の引数にマップした関数を生成します。
        これは、fastapiがpydanticをクエリとして理解しないため、関数に変換しクエリとして解釈されるように利便性を高めるために定義しました。
        モデルは以下のように解釈されます。

        class A(BaseModel):
          name: str
          age: int = 20

        def create_A(name: str, age: int = 20):
            return A(name=name, age=age)
        """
        return generate_funnel(cls)


class BaseModel(MixinModel, PydanticModel):
    class Config:
        validate_assignment = True  # 属性更新時の検証を有効にする


class BaseSettings(MixinModel, PydanticSettings):

    # TODO: test
    def to_env_file_str(self) -> str:
        """.env用の文字列を出力する"""
        prefix = getattr(self.__config__, "env_prefix", "")

        def upper(name: str):
            return name.upper()

        dic = jsonable_encoder(self)
        lines = [f"{upper(prefix + name)}={val}" for name, val in dic.items()]
        return "\n".join(lines)
