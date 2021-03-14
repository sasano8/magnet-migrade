# https://github.com/faif/python-patterns/blob/master/patterns/fundamental/delegation_pattern.py
import functools
from collections.abc import Mapping
from typing import (
    Any,
    AsyncIterable,
    AsyncIterator,
    Callable,
    Generator,
    Generic,
    Iterable,
    Iterator,
    Protocol,
    Type,
    TypeVar,
    overload,
)

from .protocols import PCancelToken, PExtender, PFuncWrapper

T = TypeVar("T")
F = TypeVar("F", bound=Callable)


class CancelToken(PCancelToken):
    def __init__(self) -> None:
        self.is_canceled = False


class Extender(PExtender[T]):
    """ある型の拡張機能群であることを表現するクラス"""

    __root__: T

    def __init__(self, __root__: T):
        self.__root__ = __root__


class Delegator(Extender[T]):
    """委任を表現するクラス"""

    def __getattr__(self, name):
        attr = getattr(self.__root__, name)
        return attr


class Undefined(Extender[None]):
    """委任を表現するクラス。テストしてないよ。一応それっぽく動く。undef is NoneでTrueを返すなど、isの挙動を調整することはpythonの仕様上できない。"""

    def __init__(self):
        self.__root__ = None

    def __bool__(self):
        return False

    def __eq__(self, other):
        return None.__eq__(other)

    def __and__(self, other):
        return None.__and__(other)

    def __xor__(self, other):
        return None.__xor__(other)

    def __or__(self, other):
        return None.__or__(other)

    def __len__(self):
        return 0

    def __abs__(self):
        return 0


class FuncMimicry(Delegator[F], PFuncWrapper[F]):
    """関数をラップし、その関数に擬態します。擬態しているため、メタプログラミングなどをすると想定外の結果を返すことがあります。
    例えば、__class__は自身のクラスでなく、functionを返します。
    """

    def __init__(self, func: F) -> None:
        super().__init__(func)
        functools.update_wrapper(self, func)
        self.__code__ = func.__code__
        self.__defaults__ = func.__defaults__  # type: ignore
        self.__kwdefaults__ = func.__kwdefaults__  # type: ignore

    @property
    def __call__(self) -> F:
        return self.__wrapped__

    @property  # type: ignore
    def __class__(self):
        return self.__wrapped__.__class__


class FuncWrapper(Extender[F]):
    @property
    def __call__(self) -> F:
        # TODO: おそらく再帰的に関数を取得するのか不明。検証が必要。⇛　取得時は１つ前を返す。呼び出し時はさかのぼってルートを呼び出す　⇛　なぜ？？？
        return self.__root__


class Generable(Iterable[T], AsyncIterable[T]):
    @overload
    def __init__(self, generator_function: Callable[..., AsyncIterator[T]]) -> None:
        ...

    @overload
    def __init__(self, generator_function: Callable[..., Iterator[T]]) -> None:
        ...

    def __init__(self, generator_function) -> None:
        self.__root__ = generator_function

    def __iter__(self, *args, **kwargs) -> Iterator[T]:
        return self.__root__(*args, **kwargs)

    def __aiter__(self, *args, **kwargs) -> AsyncIterator[T]:
        return self.__root__(*args, **kwargs)
