# from framework.utils.analyzer_pydantic import ModelFieldEx
import inspect
from dataclasses import field
from typing import Any, Dict, List, Optional, Type, TypedDict

from fastapi import Query
from pydantic import BaseConfig, BaseModel, Field
from pydantic.fields import FieldInfo, ModelField, NoArgAnyCallable, Union, Validator
from pydantic.utils import smart_deepcopy


class DataclassFieldMeta(TypedDict):
    default: Any
    default_factory: Any
    init: bool
    repr: bool
    hash: bool
    compare: bool
    metadata: Any


class PydanticFieldMeta(TypedDict):
    name: str
    type: Type
    default: Any
    default_factory: Any
    title: str
    alias: str
    description: str
    const: bool
    gt: float
    ge: float
    lt: float
    le: float
    multiple_of: float
    min_items: int
    max_items: int
    min_length: int
    max_length: int
    regex: str

    # extra
    allow_mutation: bool

    # fastapi
    deprecated: str


class ModelFieldEx:
    """https://www.apps-gcp.com/openapi_learn_the_basics/　に近づけたい"""

    kind: inspect._ParameterKind
    index: int
    description: str

    def __init__(
        self,
        *,
        name: str,
        type_: Type[Any] = Any,  # type: ignore
        kind: inspect._ParameterKind,
        default: Any = inspect._empty,  # type: ignore
        # common
        required: bool = True,
        index: int = -1,
        alias: str = None,
        description: str = "",
        meta: Any = None,
        # pydantic
        default_factory: Optional[NoArgAnyCallable] = None,
        # class_validators: Optional[Dict[str, Validator]] = None,
        # model_config: Type[BaseConfig] = BaseConfig = None,
        # field_info: Optional[FieldInfo] = None,
        # sqlalchemy
        # column_type=None,
        relation_type: str = "",  # "ONETOONE"|"MANYTOONE"|"ONETOMANY"|"MANYTOMANY"|""
        is_primary_key: bool = False,
        foreign_keys: List[str] = [],
        is_unique: bool = False,
        is_index: bool = False,
        is_nullable: bool = False,
        is_system: bool = False,
    ) -> None:
        if default is inspect._empty and not default_factory:  # type: ignore
            assert required == True

        type_ = Any if type_ is inspect._empty else type_  # type: ignore

        self.name = name
        self.type_ = type_
        # self.class_validators = class_validators
        # self.model_config = model_config
        self.default = default
        self.default_factory = default_factory
        self.required = required
        self.alias = alias or name
        # self.field_info = field_info
        self.kind = kind
        self.index = index
        self.description = description or ""
        self.meta = meta

        # orm fields
        # self.column_type = column_type
        self.foreign_keys = foreign_keys
        self.relation_type = relation_type
        self.is_primary_key = is_primary_key
        self.is_unique = is_unique
        self.is_nullable = is_nullable
        self.is_system = is_system
        self.is_index = is_index

    def get_meta_or_default(self, undefined: Any = inspect._empty) -> Any:  # type: ignore
        return self.meta or self.get_default(undefined=undefined)

    def get_real_mata(self, undefined: Any = inspect._empty) -> Any:  # type: ignore
        """定義されたままのメタ情報を取得する"""
        raise NotImplementedError()
        return self.meta

    def get_mata(self, undefined: Any = inspect._empty) -> Any:  # type: ignore
        """標準化されたpydanticのfieldinfoなどのメタ情報を取得する"""
        return self.meta

    def get_orm_mata(self, undefined: Any = inspect._empty) -> Any:  # type: ignore
        """標準化されたsqlalchemyのcolumnなどのメタ情報を取得する"""
        raise NotImplementedError()
        return self.meta

    def get_fulltextsearch_mata(self, undefined: Any = inspect._empty) -> Any:  # type: ignore
        """標準化された全文検索に関するメタを取得する"""
        raise NotImplementedError()
        return self.meta

    def get_default(self, undefined: Any = inspect._empty) -> Any:  # type: ignore
        """デフォルト値かdefault_factoryに生成されたデフォルト値かemptyを返す。emptyは任意の値を返すことができる。"""
        if self.required:
            return undefined

        # TODO:pydanticのフィールドはdeppcopｙしない。
        if isinstance(self.default, FieldInfo):
            return self.default
        return (
            self.default_factory()
            if self.default_factory
            else smart_deepcopy(self.default)
        )

    def __str__(self) -> str:
        name = self.name
        type_ = self.type_
        default = self.default
        default_factory = self.default_factory
        required = self.required
        alias = self.alias
        field_info = self.field_info
        kind = self.kind
        index = self.index
        description = self.description
        return f"{self.__class__!r}({name=},{type_=},{default=},{default_factory=},{required=},{alias=},{field_info=},{kind=},{index=},{description=})"

    @classmethod
    def from_parameter(cls, parameter: inspect.Parameter):
        return cls.from_annotation_info(
            name=parameter.name,
            annotation=parameter.annotation,
            default=parameter.default,
        )

    @classmethod
    def from_annotation_info(
        cls, name: str, annotation: Any = inspect._empty, default: Any = inspect._empty  # type: ignore
    ):
        annotation = Any if annotation is inspect._empty else annotation  # type: ignore
        parameter = inspect.Parameter(name=name, annotation=annotation, default=default)  # type: ignore
        raise NotImplementedError()

    @classmethod
    def from_pydantic_modelfield(cls, field: ModelField):
        raise NotImplementedError()
