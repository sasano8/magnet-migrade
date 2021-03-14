from __future__ import annotations

import functools
import inspect
from enum import Enum
from functools import partial, update_wrapper, wraps
from typing import (
    Any,
    Awaitable,
    Callable,
    Coroutine,
    Iterable,
    Literal,
    NamedTuple,
    Set,
    TypeVar,
)

from .analyzer_any import AnyAnalyzer
from .decorator import extensionmethod

F = TypeVar("F", bound=Callable)
ARGS = TypeVar("ARGS")
RETURN = TypeVar("RETURN")


class FuncAnalyzer(AnyAnalyzer):
    __root__: Callable

    @extensionmethod
    def get_signature(self: Callable) -> inspect.Signature:
        return inspect.signature(self)

    @extensionmethod
    def update_signature(
        self: Callable, sig: inspect.Signature, return_annotation=..., name=...
    ) -> None:
        """対象の関数をのシグネチャを与えられたシグネチャで更新します。整合性は検証されません。"""
        if not return_annotation is ...:
            sig = inspect.Signature(
                parameters=sig.parameters.values(), return_annotation=return_annotation
            )

        self.__signature__ = sig
        annotations = {}

        for p in sig.parameters.values():
            if not p.annotation is inspect._empty:  # type: ignore
                annotations[p.name] = p.annotation

        if not sig.return_annotation is inspect._empty:  # type: ignore
            annotations["return"] = sig.return_annotation

        self.__annotations__ = annotations

        __defaults__ = []
        __kwdefaults__ = {}

        for p in sig.parameters.values():
            if not p.default is inspect._empty:  # type: ignore
                if p.kind == inspect._ParameterKind.KEYWORD_ONLY:
                    __kwdefaults__[p.name] = p.default
                else:
                    # *args, **kwargsはデフォルトを設定できないので判定する必要はない
                    __defaults__.append(p.default)

        __defaults__ = tuple(__defaults__) if __defaults__ else None  # type: ignore
        __kwdefaults__ = __kwdefaults__ or None  # type: ignore

        self.__defaults__ = __defaults__
        self.__kwdefaults__ = __kwdefaults__

        if not name is ...:
            self.__name__ = name

    @extensionmethod
    def get_self_or_cls(
        self: Callable, state: Literal["auto", "bounded", "unbounded"] = "auto"
    ):
        raise NotImplementedError()

    @extensionmethod
    def wraps(self: F) -> Callable[[Callable], F]:
        from functools import wraps

        WRAPPER_ASSIGNMENTS = (
            "__module__",
            "__name__",
            "__qualname__",
            "__doc__",
            "__annotations__",
            # "__code__",  # additional
            "__defaults__",  # additional
            "__kwdefaults__",  # additional
        )
        WRAPPER_UPDATES = ("__dict__",)

        func = wraps(self, assigned=WRAPPER_ASSIGNMENTS, updated=WRAPPER_UPDATES)
        # func.__code__ = self.__code__
        return func  # type: ignore

    @extensionmethod
    def partial(self, *args, **kwargs):
        partial_func = partial(self, *args, **kwargs)
        update_wrapper(partial_func, self)
        return partial_func

    @extensionmethod
    def to_coroutine_callable(self: F) -> F:
        if FuncAnalyzer.is_coroutine_callable(self):
            return self
        elif callable(self):

            # @wraps(self)  # 非同期にすることでシグネチャが不一致になるため、ラップしていいのか検証が必要
            @FuncAnalyzer.wraps(self)
            async def wrapper(*args, **kwargs):
                return self(*args, **kwargs)

            return wrapper

        else:
            raise TypeError()

    @extensionmethod
    def normalize(self):
        raise NotImplementedError()
        # generator_function -> __iter__
        # coroutine function -> awaitable __await__
        # async generator_function -> __aiter__
