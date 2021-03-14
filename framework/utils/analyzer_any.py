import asyncio
import inspect
import re
import types
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    Dict,
    Literal,
    Type,
    _GenericAlias,
    _SpecialForm,
    get_type_hints,
)

from .decorator import extensionmethod


class Extension:
    __root__: Any

    def __init__(self, __root__) -> None:
        self.__root__ = __root__


class AnyAnalyzer(Extension):
    __root__: Any

    # @extensionmethod
    # def get_annotations(self) -> Dict[str, Type]:
    #     """
    #     get_type_hintsを使ってください。
    #     __annotations__を取得する。pythonのデフォルトの挙動は基底クラスのannotationsを包含していないので、全ての基底クラスを辿ったannotationsを取得する。
    #     """
    #     if inspect.isfunction(self):
    #         return getattr(self, "__annotations__", {})
    #     else:
    #         annotations = {}

    #     classes = inspect.getmro(self)[:-1]  # 最後はオブジェクトなので不要
    #     for base in reversed(classes):
    #         if tmp := getattr(base, "__annotations__", None):
    #             annotations.update(tmp)
    #     return annotations

    @extensionmethod
    def get_type_hints(self) -> Dict[str, Type]:
        """__annotations__をmroを辿り前方参照を解決した辞書を返す。ただし、全ての前方参照が解決できているとは限らない。"""
        return get_type_hints(self)

    # @extensionmethod
    # def get_type_hints_from_current_frame(self) -> Dict[str, Type]:
    #     frame = inspect.currentframe()
    #     l = frame.f_back.f_locals  # ["local_vars"]
    #     g = frame.f_back.f_globals  # ["global_vars"]
    #     return get_type_hints(self, g, l)

    @extensionmethod
    def get_type_hints_from_current_frame(self, count: int = 0) -> Dict[str, Type]:
        if count < 0:
            raise ValueError()

        root = inspect.currentframe()
        current = root
        for i in range(count + 1):
            current = current.f_back  # type: ignore

        l = current.f_locals  # type: ignore
        g = current.f_globals  # type: ignore
        return get_type_hints(self, g, l)

    @extensionmethod
    def get_signature(self, frame_count: int = 0):
        if frame_count < 0:
            raise ValueError()

        # TODO: python3.10でsignatureがget_type_hintsで解析されるので、それに乗り換える

        sig = inspect.signature(self)
        annotations = AnyAnalyzer.get_type_hints_from_current_frame(
            self, frame_count + 1
        )

        def yield_parameters():
            for param in sig.parameters.values():
                yield inspect.Parameter(
                    name=param.name,
                    kind=param.kind,
                    default=param.default,
                    annotation=annotations.get(param.name, param.annotation),
                )

        return inspect.Signature(
            parameters=yield_parameters(), return_annotation=sig.return_annotation
        )

    @extensionmethod
    def get_type(self):
        return type(self)

    # @extensionmethod
    # def get_signature(self: Callable) -> inspect.Signature:  # type: ignore
    #     return inspect.signature(self)

    @extensionmethod
    def is_instance(self, typ: Type) -> bool:
        return isinstance(self, typ)

    @extensionmethod
    def is_subclass(self: Type, cls: Type) -> bool:  # type: ignore
        return issubclass(self, cls)

    @extensionmethod
    def is_function(self) -> bool:
        return inspect.isfunction(self)

    @extensionmethod
    def is_coroutine(self) -> bool:
        return inspect.iscoroutine(self)

    @extensionmethod
    def is_coroutine_function(self) -> bool:
        """非推奨。is_coroutine_callableを利用してください。__call__を認識しません。"""
        return inspect.iscoroutinefunction(self)

    @extensionmethod
    def is_coroutine_callable(self):
        if inspect.iscoroutinefunction(self):
            return True

        if func := getattr(self, "__call__", None):
            return inspect.iscoroutinefunction(func)
        else:
            return False

    @extensionmethod
    def is_asyncgenerator_callable(self):
        if inspect.isasyncgenfunction(self):
            return True

        if func := getattr(self, "__call__", None):
            return inspect.isasyncgenfunction(func)
        else:
            return False

    @extensionmethod
    def is_generator_callable(self):
        if inspect.isgeneratorfunction(self):
            return True

        if func := getattr(self, "__call__", None):
            return inspect.isgeneratorfunction(func)
        else:
            return False

    @extensionmethod
    def is_awaitable(self) -> bool:
        return inspect.isawaitable(self)

    @extensionmethod
    def is_future(self) -> bool:
        return asyncio.isfuture(self)

    @extensionmethod
    def is_generatorfunction(self) -> bool:
        return inspect.isgeneratorfunction(self)

    @extensionmethod
    def is_method(self) -> bool:
        return inspect.ismethod(self)

    @extensionmethod
    def is_static_method(self) -> bool:
        return isinstance(self, staticmethod)

    @extensionmethod
    def is_unbounded_method(self) -> bool:
        """
        クラス内関数にデコレータを付与した場合、インスタンス生成前後の関数とメソッドを意識しなければならない。
        第一引数にselfまたはclsを持つ関数をメソッドとして判定する。
        selfとclsの名前は、別名を名付けることができるため、確実に判定できる保証がないが、この方法しかないと思われる。

        インスタンスが作成され、関数がインスタンスにバインドされたfunctionをmethodと呼ぶが、
        inspectモジュールは、クラス定義時におけるメソッドはただのfunctionとして判定するため、
        クラス定義時にis_methodを代替する関数が必要となった。
        """
        obj = AnyAnalyzer(self)

        # TODO: _get__を持つオブジェクトも関数の可能性がある

        if not obj.is_function():
            return False

        if obj.is_static_method():
            return False
        elif obj.is_method():
            return False

        args = list(inspect.signature(self).parameters.items())
        if not len(args):
            return False

        key, value = args[0]
        if key in {"self", "cls"}:
            return True
        else:
            return False

    @extensionmethod
    def is_callable(self) -> bool:
        return callable(self)

    @extensionmethod
    def is_descriptor(self) -> bool:
        return hasattr(self, "__get__")

    @extensionmethod
    def get_belong_qual_name(self) -> str:
        """自身を除いた__qualname__を返す"""
        # インスタンスが作成され、関数がインスタンスにバインドされるまではメソッドであるか分からないため、クラスに属した関数かチェックする
        qualname_arr = self.__qualname__.split(".")
        del qualname_arr[-1]  # delete last element(self).
        return ".".join(qualname_arr)

    @extensionmethod
    def is_class_attr(self) -> bool:
        s = AnyAnalyzer.get_belong_qual_name(self)
        if s == "":
            return False

        if re.search(r"<locals>", s):
            raise Exception("ローカルスコープのオブジェクトは解析できません")

        return True

    @extensionmethod
    def is_generic_type(self, typ: _GenericAlias = Any):
        raise NotImplementedError()
        if isinstance(self, _GenericAlias):
            is_generic = 1
        elif isinstance(self, _SpecialForm):
            is_generic = 2
        else:
            return False

        if is_generic:

            if not hasattr(self, "__origin__"):
                return False

        if self.__origin__ is typ:
            return True
        else:
            return False

    @extensionmethod
    def is_literal(self):
        if not isinstance(self, _GenericAlias):
            return False

        if self.__origin__ is Literal:
            return True
        else:
            return False
