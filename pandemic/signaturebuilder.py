from __future__ import annotations

import functools
import inspect
from collections import defaultdict
from types import MappingProxyType
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Protocol,
    Set,
    Type,
    TypeVar,
    Union,
)

from pydantic import BaseModel

from framework import Linq
from framework.analyzers import AnyAnalyzer, FuncAnalyzer

from .field import ModelFieldEx
from .normalizers import Adapters, Normalizers, Unpackers

T = TypeVar("T")


class PSignature(Protocol):
    @property
    def parameters(self) -> MappingProxyType[str, inspect.Parameter]:
        raise NotImplementedError()

    @property
    def return_annotation(self) -> Any:
        raise NotImplementedError()


class SignatureBuilder:
    """シグネチャで欠落してしまう情報を保持し、様々なライブラリに対応するシグネチャ変換メソッドを提供する"""

    __normalizer__ = Normalizers
    __adapter__ = Adapters
    __unpacker__ = Unpackers

    def __init__(
        self,
        parameters: Dict[str, ModelFieldEx],  # dictじゃなくてlistでいい
        return_annotation: Type = None,
        processor: Callable = None,
        binder: Union[Callable, None] = None,
        model: Type = None,
        name: str = None,
        description: str = "",
    ):
        if not model and not processor:
            raise Exception()

        if model and not processor:
            processor = model
            name = name or model.__name__
            return_annotation = return_annotation or model
        elif not model and processor:
            name = name or processor.__name__
            return_annotation = return_annotation or Any  # type: ignore

        self.parameters = parameters
        self.model = model
        self.processor = processor
        self.binder = binder
        self.name = name
        self.return_annotation = (
            Any if return_annotation is inspect._empty else return_annotation  # type: ignore
        )
        self.description = description

    def __eq__(self, other):
        """シグネチャを持つオブジェクトと比較を行う"""
        raise NotImplementedError()

    @classmethod
    def try_get_signature(cls, obj) -> Union[None, SignatureBuilder]:
        raise NotImplementedError()

    def copy(self, **updates) -> SignatureBuilder:
        dic = {
            "model": self.model,
            "processor": self.processor,
            "binder": self.binder,
            "name": self.name,
            "return_annotation": self.return_annotation,
            "description": self.description,
            "parameters": self.parameters,
            **updates,
        }

        return self.__class__(**dic)  # type: ignore

    def unpack_recursive(self) -> SignatureBuilder:
        """アンパック可能な限り再帰的にアンパックを行う"""
        raise NotImplementedError()

    def raise_if_cant_unpack(self, forbidden=None):
        forbidden_filter = forbidden or self.__class__.__unpacker__.filter_forbidden
        forbbidens = [field for field in self.get_fields() if forbidden_filter(field)]
        if len(forbbidens):
            invalids = [x.name for x in forbbidens]
            raise AssertionError(f"{forbidden_filter.__doc__} -> {invalids}")

    def get_fields(self) -> Iterator[ModelFieldEx]:
        for field in self.parameters.values():
            yield field

    def get_unpackable_fields(self, unpacker=None) -> Iterator[ModelFieldEx]:
        unpack_filter = unpacker or self.__class__.__unpacker__.filter_default
        yield from (field for field in self.get_fields() if unpack_filter(field))

    def unpack(self, unpacker=None, forbidden=None) -> SignatureBuilder:
        """"""
        forbidden_filter = forbidden or self.__class__.__unpacker__.filter_forbidden
        unpack_filter = unpacker or self.__class__.__unpacker__.filter_default

        self.raise_if_cant_unpack(forbidden_filter)
        unpackables = {x.name: x for x in self.get_unpackable_fields(unpack_filter)}

        if not len(unpackables):
            return self

        def get_unpacalbes_nest_parameters():
            for name, field in unpackables.items():
                sb = match_type_and_process(field.type_)
                yield name, {x.name: x for x in sb.get_fields()}

        root_parameters = {field.name: field for field in self.get_fields()}
        nest_parameters = {
            name: parameters for name, parameters in get_unpacalbes_nest_parameters()
        }

        # アンパック対象となった引数名と、展開後の引数名群
        extracted_args = {
            name: set(fields.keys()) for name, fields in nest_parameters.items()
        }

        # アンパック対象となった引数名と、ファクトリーを返す。現在は、BaseModelクラスを返している
        factories = {
            name: param.type_
            for name, param in root_parameters.items()
            if name in extracted_args
        }

        # 展開された引数をファクトリ関数で元に戻す
        restore = functools.partial(
            self.restore_args,
            extracted_args=extracted_args,
            factories=factories,
        )

        # 渡された引数が可変長引数である場合に、元の位置へ戻す
        split = functools.partial(
            self.split_args,
            src_parameters=self.get_signature().parameters,
        )

        # 親のbinderが存在する場合に
        def binder(*args, **kwargs):
            kwargs = restore(**kwargs)
            return split(*args, **kwargs)

        new_fields: Dict[str, ModelFieldEx] = self.join_fields(
            {x.name: x for x in self.get_fields()}, nest_parameters
        )

        builder = self.copy(
            parameters=new_fields,
            binder=binder,
            processor=self.processor,  # TODO: これだと多重アンパックした際に動かなくなる。unpack時にbinderが存在する場合は、processorをbuildして保存しておく必要がある。もしくは、binderだけをネストさせていくか
        )

        return builder

    def infer(self) -> SignatureBuilder:
        """型がAnyの場合、デフォルト値から型を推論し、新たなインスタンスを返します。"""
        raise NotImplementedError()

    @classmethod
    def join_fields(
        cls,
        root_parameters: Dict[str, ModelFieldEx],
        nest_parameters: Dict[str, Dict[str, ModelFieldEx]],
        conflict_validator=None,
    ) -> Dict[str, ModelFieldEx]:
        conflict_validator = (
            conflict_validator or cls.__unpacker__.assert_if_conflict_field_name
        )
        root = Linq(
            param
            for name, param in root_parameters.items()
            if not name in nest_parameters
        )

        def yield_fields():
            for fields in nest_parameters.values():
                for field in fields.values():
                    yield field

        fields = root.chain(yield_fields()).to_list()
        if conflict_validator(fields):
            query = Linq(fields).distinct(lambda x: x.name)
        else:
            query = fields

        return {field.name: field for field in sorted(query, key=lambda x: x.kind)}

    @staticmethod
    def restore_args(
        extracted_args: Dict[str, Set[str]],
        factories: Dict[str, Callable],
        **kwargs,
    ):
        """展開された引数を元の引数の型に復元し、キーワード引数を展開前の引数に適合させる"""
        created_objects = {}
        for name, unpacked_args in extracted_args.items():
            dic = {x: kwargs[x] for x in unpacked_args if x in kwargs}
            created_objects[name] = factories[name](**dic)

        for unpacked_args in extracted_args.values():
            for name in unpacked_args:
                kwargs.pop(name, None)

        # 引数名が衝突した時、エラーが発生する。そんなことはあるのか？
        return dict(**kwargs, **created_objects)

    @staticmethod
    def split_args(
        src_parameters: Dict[str, inspect.Parameter],
        *args,
        **kwargs,
    ):
        """展開前の引数型に復元された変数の位置を調整する"""
        new_args = list(args)
        size = len(args)
        for index, field in enumerate(src_parameters.values()):
            # ソースパラメータはSignatureの検証により、有効な順序に並んでいることが保証されている
            # パラメータは定義されている引数の順序で列挙されるのでソートは不要
            # TODO: pandemicの仕様として、パラメータに可変長位置引数と可変長キーワード引数は含まれていないことが保証されている（現在は実装していない）

            # POS順に並んでいるので単に追加していけばよい
            if field.kind == inspect._ParameterKind.POSITIONAL_ONLY:
                if index < size:
                    val = kwargs.pop(field.name)
                    new_args.insert(index, val)
                else:
                    val = kwargs.pop(field.name)
                    new_args.append(val)
            elif field.kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD:
                if index < size:
                    val = kwargs.pop(field.name)
                    new_args.insert(index, val)
                else:
                    # キーワード引数のままでOK
                    break
            else:
                break
        return new_args, kwargs

    @classmethod
    def unpack_arguments(
        cls,
        adapter: Callable[[ModelFieldEx], inspect.Parameter] = None,
        **adapter_options,
    ) -> Callable[[Callable], Callable]:
        """関数の引数を展開し、指定したアダプタで生成されたシグネチャでラップされた関数を返します。デフォルトのアダプタは、ベストエフォートで純粋な定義を返します。"""

        def wrapped(func: Callable) -> Callable:
            sig = cls.from_func(func).unpack()
            func = sig.get_func(adapter, **adapter_options)

            return func

        return wrapped

    def get_signature(
        self,
        adapter: Callable[[ModelFieldEx], inspect.Parameter] = None,
        **adapter_options,
    ):
        """任意のマッピングでシグネチャを生成する。マッピングを指定しない場合は、定義されているままのシグネチャを返す"""
        adapter = adapter or self.__class__.__adapter__.to_general
        mapping = map(
            functools.partial(adapter, **adapter_options), self.parameters.values()
        )
        return inspect.Signature(
            parameters=mapping,  # type: ignore
            return_annotation=self.return_annotation,
        )

    # Finalizer
    def get_func(
        self,
        adapter: Callable[[ModelFieldEx], inspect.Parameter] = None,
        **adapter_options,
    ):
        wrapped = self._generate_func()
        created_sig = self.get_signature(adapter, **adapter_options)
        FuncAnalyzer.update_signature(wrapped, sig=created_sig, name=self.name)
        return wrapped

    def _generate_func(self):
        processor = self.processor
        binder = self.binder
        if binder:

            if inspect.iscoroutinefunction(processor):

                async def wrapped(*args, **kwargs):
                    args, kwargs = binder(*args, **kwargs)  # type: ignore
                    return await processor(*args, **kwargs)  # type: ignore

            else:

                def wrapped(*args, **kwargs):
                    args, kwargs = binder(*args, **kwargs)  # type: ignore
                    return processor(*args, **kwargs)  # type: ignore

        else:
            if inspect.iscoroutinefunction(processor):

                async def wrapped(*args, **kwargs):
                    return await processor(*args, **kwargs)  # type: ignore

            else:

                def wrapped(*args, **kwargs):
                    return processor(*args, **kwargs)  # type: ignore

        return wrapped

    def get_pydantic(self, mapper: Callable[[ModelFieldEx], inspect.Parameter] = None):
        raise NotImplementedError()

    def get_sqlalchemy(
        self, mapper: Callable[[ModelFieldEx], inspect.Parameter] = None
    ):
        raise NotImplementedError()

    def get_sqlalchemy_base(
        self, mapper: Callable[[ModelFieldEx], inspect.Parameter] = None
    ):
        """ベースメタデータを解析し、テーブルの一覧を取得する。"""
        raise NotImplementedError()

    ##############
    # importer
    ##############
    @classmethod
    def from_func(
        cls, func: Callable, normalizer=None, frame_count: int = 0
    ) -> SignatureBuilder:
        normalize = normalizer or cls.__normalizer__.from_parameter
        # sig = inspect.signature(func)
        sig = AnyAnalyzer.get_signature(func, frame_count + 1)

        parameters = (
            normalize(field, index)
            for index, field in enumerate(sig.parameters.values())
        )

        return SignatureBuilder(
            parameters={param.name: param for param in parameters},
            return_annotation=sig.return_annotation,
            processor=func,
        )

    @classmethod
    def from_basemodel(
        cls, basemodel: Type[BaseModel], normalizer=None
    ) -> SignatureBuilder:
        normalize = normalizer or cls.__normalizer__.from_modelfield
        __annotations__ = AnyAnalyzer.get_type_hints(basemodel)

        fields = (
            normalize(field, index, annotations=__annotations__)
            for index, field in enumerate(basemodel.__fields__.values())
        )

        return SignatureBuilder(
            parameters={field.name: field for field in fields},
            return_annotation=basemodel,
            processor=basemodel,
        )

    @classmethod
    def from_django(cls, model, normalizer=None) -> SignatureBuilder:
        raise NotImplementedError()

    @classmethod
    def from_dataclass(cls, dc: Type, normalizer=None) -> SignatureBuilder:
        raise NotImplementedError()

    @classmethod
    def from_sqlalchemy_declarative_base(cls, base) -> List[SignatureBuilder]:
        from sqlalchemy.orm import mapperlib

        # mappers = [x for x in mapperlib._mapper_registry]
        # target_mappers = [x for x in mappers if x.selectable.metadata is base.metadata]
        # return [
        #     cls.from_sqlalchemy_model(table._identity_class) for table in target_mappers
        # ]

        return [
            cls.from_sqlalchemy_model(table._identity_class)
            for table in base.registry.mappers  # sorted(
            # enumerate(base.registry.mappers), key=lambda x: x[0], reverse=True
            # )  # 定義順の逆で返ってくるっぽいので元に戻す
        ]

    @classmethod
    def from_sqlalchemy_model(cls, model, normalizer=None) -> SignatureBuilder:
        normalize = normalizer or cls.__normalizer__.from_sqlalchemy_column
        parameters = (
            normalize(field, index)
            for index, field in enumerate(model._sa_class_manager.local_attrs.values())
        )

        return SignatureBuilder(
            parameters={param.name: param for param in parameters},
            return_annotation=model,
            model=model,
            name=model.__name__,
        )

    @classmethod
    def from_namedtuple(cls, model) -> SignatureBuilder:
        raise NotImplementedError()

    @classmethod
    def from_typeddict(cls, model) -> SignatureBuilder:
        raise NotImplementedError()

    @classmethod
    def from_dict(cls, instance: dict, name: str = "DynamicModel") -> SignatureBuilder:
        """辞書インスタンスを解析し、シグネチャを生成します。型推論は、pydanticによって行われます。"""
        from pydantic import BaseConfig, create_model

        # TODO: libs.generatorを削除する
        class Config(BaseConfig):
            schema_extra = {"example": instance}

        model = create_model(name, __config__=Config, **instance)
        return cls.from_basemodel(model)

    @classmethod
    def from_json(cls, json: str) -> SignatureBuilder:
        """json文字列を解析し、シグネチャを生成します。型推論は、pydanticによって行われます。"""
        raise NotImplementedError()

    @classmethod
    def from_yml(cls, yml: str) -> SignatureBuilder:
        """json文字列を解析し、シグネチャを生成します。型推論は、pydanticによって行われます。"""
        raise NotImplementedError()

    @classmethod
    def from_module(cls, module) -> List[SignatureBuilder]:
        """モジュールの属性を走査し、解析に成功した属性群をSignatureBuilderで返します。"""
        raise NotImplementedError()

    @classmethod
    def from_package(cls, module) -> List[SignatureBuilder]:
        """パッケージの属性を走査し、解析に成功した属性群をSignatureBuilderで返します。"""
        raise NotImplementedError()


def match_type_and_process(type_) -> SignatureBuilder:
    if inspect.isclass(type_) and issubclass(type_, BaseModel):
        return SignatureBuilder.from_basemodel(type_)
    else:
        raise TypeError(f"Unsupport unpack type: {type_}")
