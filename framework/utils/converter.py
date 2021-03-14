from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from functools import partial
from inspect import Signature
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Tuple,
    Type,
    _GenericAlias,
    get_args,
)

from framework.utils.decorator import compatibility, extensionmethod


@dataclass
class Converter:
    __root__: Any

    @extensionmethod
    def pydantic_to_func(self):
        raise NotImplementedError()

    @extensionmethod
    def func_to_sig(self: Callable):  # type: ignore[misc]
        raise NotImplementedError()

    @extensionmethod
    def sig_to_sig_and_normalize(self: Signature):
        """シグネチャの型をビルトイン型へ変換する。変換はベストエフォートで行われる。"""
        raise NotImplementedError()

    @extensionmethod
    def sig_to_sig_and_unpack_pydantic(self: Signature):
        """入力される型がpydanticの場合、pydanticの属性を引数に展開します。"""
        raise NotImplementedError()

    @extensionmethod
    def sig_to_pydantic(self: Signature):  # type: ignore[misc]
        raise NotImplementedError()

    @extensionmethod
    def sig_to_sig_for_fastapi(self: Signature):  # type: ignore[misc]
        raise NotImplementedError()

    @extensionmethod
    def sig_to_sig_for_typer(self: Signature):  # type: ignore[misc]
        raise NotImplementedError()

    @extensionmethod
    def sig_to_code(self: Signature):
        raise NotImplementedError()

    @compatibility((3, 8))
    @extensionmethod
    def extract_sig_pos_only(self: Signature):
        raise NotImplementedError()

    @extensionmethod
    def extract_sig_kw_only(self: Signature):
        raise NotImplementedError()

    @extensionmethod
    def extract_sig_pos_or_kw(self: Signature):
        # extract_sig_pos_only +     def extract_sig_kw_only(self: Signature):
        raise NotImplementedError()

    @compatibility((3, 7))
    @extensionmethod
    def literal_to_enum(self, name: str = "LiteralEnum"):
        literal = self
        # python ^3.7
        if not isinstance(literal, _GenericAlias):
            raise TypeError()

        if not literal.__origin__ is Literal:
            raise TypeError()

        class ClassDict(dict):
            def __init__(self, iterable):
                super().__init__(iterable)
                self._member_names = list(self.keys())

        args = get_args(literal)
        dic = {str(val): str(val) for val in args}
        classdict = ClassDict(dic)
        enum_ = type(name, (str, Enum), classdict)

        return enum_

    @extensionmethod
    def enum_to_dict(obj: Type[Enum]) -> dict:  # type: ignore[misc]
        if not issubclass(obj, Enum):
            raise TypeError

        _member_map_: dict = obj._member_map_  # type: ignore[assignment]
        return {k: v.value for k, v in _member_map_.items()}
