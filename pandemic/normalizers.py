import inspect
from collections import defaultdict
from typing import Any, Dict, Iterable, List, Tuple, Type, Union

from fastapi import Query
from fastapi.params import Body, Depends, Param
from pydantic.fields import FieldInfo, ModelField
from pydantic.main import BaseModel
from sqlalchemy.orm import ColumnProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.orm.relationships import RelationshipProperty
from typer import Argument, Option

from framework import MappingDict, udict
from framework.analyzers import AnyAnalyzer
from framework.converters import Converter

from .field import ModelFieldEx


class Unpack:
    """このクラスを継承したBaseModelはクエリパラメータとして展開されます。"""

    pass


class Normalizers:
    @staticmethod
    def from_parameter(param: inspect.Parameter, index=0, **extra) -> ModelFieldEx:
        """シグネチャのパラメータを正規化する"""
        required = True if param.default is inspect._empty else False  # type: ignore
        default = inspect._empty if required else param.default  # type: ignore
        type_ = Any if param.annotation is inspect._empty else param.annotation  # type: ignore

        return ModelFieldEx(
            name=param.name,
            type_=type_,
            # class_validators=None,
            default=param.default,
            default_factory=None,
            required=required,
            alias=None,
            kind=param.kind,
            index=index,
            meta=None,
        )

    @staticmethod
    def from_modelfield(
        field: ModelField,
        index=0,
        annotations: Dict[str, Type] = None,
        **extra,
    ) -> ModelFieldEx:
        """pydanticのfieldを正規化する"""
        default = inspect._empty if field.required else field.default  # type: ignore

        # field.type_は特殊な型に変換されていることがあるので、inspect.signatureで元の型を取得する
        # 例えば、int型のFieldに長さ制限などを設けると、ConstrainedIntValueにビルドされる。
        annotations = annotations or {}
        type_ = annotations.get(field.name, Any)

        if field.name != field.alias:
            additional = udict()
            additional["alias"] = field.alias

            # これらはfastapi独自の属性のため、extraに格納されていない
            if isinstance(field.field_info, (Body, Param)):
                additional.fetch_attr(field.field_info, "deprecated")
                additional.fetch_attr(field.field_info, "convert_underscores")
                additional.fetch_attr(field.field_info, "embed")
                additional.fetch_attr(field.field_info, "media_type")

            kwargs = dict(field.field_info.__repr_args__())  # dict(key_value_paris)
            extra = kwargs.pop("extra")  # kwargs = { 'default', Ellipsis, 'extra': {}}
            kwargs.update(**extra, **additional)
            field_info = field.field_info.__class__(**kwargs)  # type: ignore

        else:
            # BodyとQueryなど継承クラスの場合は、情報を落とすとまずいのでそのまま
            if field.field_info.__class__ is not FieldInfo:
                field_info = field.field_info
            else:
                kwargs = dict(field.field_info.__repr_args__())  # dict(key_value_paris)
                extra = kwargs.pop(
                    "extra"
                )  # kwargs = { 'default', Ellipsis, 'extra': {}}
                kwargs.update(**extra)

                # デフォルト値のみのFieldInfoは定義されていないものとみなす
                if len(kwargs) <= 1:
                    field_info = None  # type: ignore
                else:
                    field_info = field.field_info

        return ModelFieldEx(
            name=field.name,
            type_=type_,
            # class_validators=field.class_validators,
            # model_config=field.model_config,
            default=default,
            default_factory=field.default_factory,
            required=field.required,
            alias=field.alias,
            meta=field_info,
            kind=inspect._ParameterKind.KEYWORD_ONLY,
            index=index,
            description=field.field_info.description,
        )

    @staticmethod
    def from_sqlalchemy_column(
        column: InstrumentedAttribute, index=0, **extra
    ) -> ModelFieldEx:
        # """
        # 'key',
        # 'name',
        # 'table',
        # 'type',
        # 'is_literal',
        # 'primary_key',
        # 'nullable',
        # 'default',
        # 'server_default',
        # 'server_onupdate',
        # 'index',
        # 'unique',
        # 'system',
        # 'doc',
        # 'onupdate',
        # 'autoincrement',
        # 'constraints',
        # 'foreign_keys',
        # 'comment',
        # 'computed',
        # '_creation_order',
        # 'dispatch',
        # 'proxy_set',
        # 'description',
        # 'comparator',
        # '_cloned_set',
        # '_from_objects',
        # '_label',
        # '_key_label',
        # '_render_label_in_columns_clause'
        # """
        # https://github.com/tiangolo/pydantic-sqlalchemy/blob/master/pydantic_sqlalchemy/main.py

        python_type = Any
        relation_type = ""
        is_virtual = False

        if isinstance(column.property, ColumnProperty):
            # name = column.name
            name = column.name
            # column_type = column.type
            # target = column
            python_type = column.type.python_type
            required = column.default is None and not column.nullable
            required = True if column.primary_key else required
            default = column.default
            comment = column.comment or ""
            is_primary_key = True if column.primary_key else False
            is_nullable = True if column.nullable else False
            is_index = True if column.index else False
            is_unique = True if column.unique else False
            is_system = True if column.system else False

            foreign_keys = [x._colspec for x in column.expression.foreign_keys]
        elif isinstance(column.property, RelationshipProperty):
            is_virtual = True
            name = column.key
            # column_type = column

            relation_type = column.property.direction.name

            if relation_type == "ONETOONE":
                python_type = column.property.entity._identity_class
            elif relation_type == "MANYTOONE":
                python_type = column.property.entity._identity_class
            elif relation_type == "ONETOMANY":
                python_type = Iterable[column.property.entity._identity_class]  # type: ignore
            elif relation_type == "MANYTOMANY":
                python_type = Iterable[column.property.entity._identity_class]  # type: ignore
            else:
                raise Exception()

            required = True
            default = None
            comment = ""
            is_primary_key = False
            is_nullable = False
            is_index = False
            is_unique = False
            is_system = False
            foreign_keys = [
                x._colspec for x in column.property._user_defined_foreign_keys
            ]  # 合ってるか分からない
        else:
            raise Exception()

        return ModelFieldEx(
            name=name,
            type_=python_type,  # type: ignore
            required=required,
            # class_validators=None,
            # model_config=None,  # type: ignore
            default=default,
            default_factory=None,
            alias=None,
            meta=column,
            kind=inspect._ParameterKind.KEYWORD_ONLY,
            index=index,
            description=comment,
            # column_type=column,
            relation_type=relation_type,
            foreign_keys=foreign_keys,
            is_primary_key=is_primary_key,
            is_nullable=is_nullable,
            is_index=is_index,
            is_unique=is_unique,
            is_system=is_system,
        )


class Unpackers:
    """アンパック対象となる型フィルタを定義する"""

    @staticmethod
    def assert_if_conflict_field_name(fields: Iterable[ModelFieldEx]) -> bool:
        dic: Dict[str, List[ModelFieldEx]] = defaultdict(list)
        for item in fields:
            dic[item.name].append(item)

        for name, values in dic.items():
            if len(values) > 1:
                raise AssertionError(f"Conflict field name: {name}")

        return False

    @staticmethod
    def filter_forbidden(field: ModelFieldEx) -> bool:
        """Can't unpack for contains POSITIONAL_ONLY or VAR_POSITIONAL or VAR_KEYWORD."""
        kind = field.kind
        return (
            kind == inspect._ParameterKind.POSITIONAL_ONLY
            or kind == inspect._ParameterKind.VAR_POSITIONAL
            or kind == inspect._ParameterKind.VAR_KEYWORD
        )

    @staticmethod
    def filter_default(field: ModelFieldEx) -> bool:
        """デフォルトのアンパック挙動を定義する。"""
        if (
            field.required
            and not inspect.isfunction(field.type_)
            and inspect.isclass(field.type_)
            and issubclass(field.type_, BaseModel)
        ):
            return True
        else:
            return False

    @staticmethod
    def filter_fastapi(field: ModelFieldEx) -> bool:
        """fastapi用のアンパック挙動を定義する。

        # 前置き
        fastapiは引数にBaseModelが与えられた時、それをリクエストボディとして認識する。（GET時のリクエストボディは一般的ではないが、リクエストボディとして認識するようだ。）
        それ以外の引数（Depends等を除く）は、クエリパラメータもしくはパスパラメータとなる。

        # 仕様
        # Unpackを継承した型を展開対象とする。それらは、クエリパラメータとして展開される。
        """
        if (
            field.required
            and not inspect.isfunction(field.type_)
            and inspect.isclass(field.type_)
            and issubclass(field.type_, Unpack)
        ):
            if issubclass(field.type_, BaseModel):
                if not field.type_.__config__.allow_population_by_field_name:
                    raise ValueError(
                        "Must be BaseModel.Config.allow_population_by_field_name = True. for use alias."
                    )

            return True
        else:
            return False


class Adapters:
    @staticmethod
    def to_general(field: ModelFieldEx, options: dict = {}) -> inspect.Parameter:
        default = field.get_meta_or_default(undefined=inspect._empty)  # type: ignore
        return inspect.Parameter(
            name=field.name, kind=field.kind, default=default, annotation=field.type_
        )

    @staticmethod
    def to_fastapi(field: ModelFieldEx, options: dict = {}) -> inspect.Parameter:
        meta: Any = field.get_mata(undefined=None)
        default: Any

        if meta:
            if isinstance(meta, Depends):
                default = meta
            elif isinstance(meta, FieldInfo):
                default = meta
            else:
                raise TypeError(f"unkwon type meta: {meta}")
        else:
            default = field.get_default(undefined=inspect._empty)  # type: ignore

        if default.__class__ is FieldInfo:
            kwargs = dict(default.__repr_args__())  # dict(key_value_paris)
            extra = kwargs.pop("extra")  # kwargs = { 'default', Ellipsis, 'extra': {}}
            default = Query(**kwargs, **extra)

        return inspect.Parameter(
            name=field.name,
            kind=field.kind,
            default=default,
            annotation=field.type_,
        )

    @staticmethod
    def to_typer(field: ModelFieldEx, **options) -> inspect.Parameter:
        meta = field.get_mata(None)
        default = field.get_default(undefined="")

        if AnyAnalyzer(field.type_).is_literal():
            type_ = Converter.literal_to_enum(field.type_)
            default = type_(default)
        else:
            type_ = field.type_

        class Extract(MappingDict):
            allow_extra = False
            from_to = {"description": "help", "envvar": "envvar"}

        kwargs = Extract()
        kwargs.fetch_attr(meta, "description")
        if extra := getattr(meta, "extra", None):
            if env_names := extra.get("env_names", None):
                kwargs["envvar"] = next(iter(env_names))

        kwargs = {**options, **kwargs}  # type: ignore

        if field.required and not "prompt" in kwargs:
            default = Argument(..., **kwargs) if kwargs else inspect._empty
        else:
            default = Option(default, **kwargs) if kwargs else default

        return inspect.Parameter(
            name=field.name,
            kind=field.kind,
            default=default,
            annotation=type_,
        )

    @staticmethod
    def to_pydantic(field: ModelFieldEx, options: dict = {}) -> inspect.Parameter:
        raise NotImplementedError()
