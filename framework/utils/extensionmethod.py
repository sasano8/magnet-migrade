from functools import partial, wraps
from types import FunctionType, MethodType
from typing import Any, Callable, Generic, Protocol, Type, TypeVar, Union

# https://docs.python.org/3/howto/descriptor.html#functions-and-methods
# https://stackoverflow.com/questions/6685232/how-are-methods-classmethod-and-staticmethod-implemented-in-python
# https://hg.python.org/cpython/file/69b416cd1727/Objects/funcobject.c

T = TypeVar("T")


class ExtensionMethodFactory:
    def __call__(self, func: T, /, *, bind="__root__", decorator: Callable = None) -> T:
        if decorator:
            func = decorator(func)
        return ExtensionMethod.instantiate(func, bind=bind)

    def option(
        self, bind: str = "__root__", decorator: Callable = None
    ) -> Callable[[T], T]:
        return partial(self.__call__, bind=bind, decorator=decorator)  # type: ignore[return-value]


class ExtensionMethod:
    @classmethod
    def instantiate(cls, func, *, bind: str = "__root__"):
        self = cls(func=func, bind=bind)
        return wraps(func)(self)

    def __init__(self, func, *, bind: str = "__root__"):
        self.__func__ = func
        self.__root__ = bind

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.__func__
        func = self.__func__
        __root__ = self.__root__

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(getattr(self, __root__), *args, **kwargs)

        return MethodType(wrapper, obj)

    def __call__(self, __root__, *args, **kwargs):
        return self.__func__(__root__, *args, **kwargs)
