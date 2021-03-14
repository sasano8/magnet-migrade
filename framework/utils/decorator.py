import sys
from typing import Any, Callable, Tuple, TypeVar

from .extensionmethod import ExtensionMethodFactory

T = TypeVar("T")

extensionmethod: ExtensionMethodFactory = ExtensionMethodFactory()


def compatibility(version: Tuple[int], replace: Any = None) -> Callable[[T], T]:
    """指定したバージョン未満の場合に関数を無効化する。もしくは、新たな関数で置き換える。"""

    def disable(func: T) -> T:
        if sys.version_info >= version:
            return func
        else:
            return replace  # type: ignore

    return disable


def deprecated(func: T) -> T:
    return func
