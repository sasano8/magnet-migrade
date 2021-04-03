from typing import Callable, Generic, Protocol, TypeVar

T = TypeVar("T")
F = TypeVar("F", bound=Callable, covariant=True)


class PExtender(Protocol[T]):
    __root__: T


class PCancelToken(Protocol):
    is_cancelled: bool

    @property
    def is_cancelled(self):
        raise NotImplementedError()


class PFuncWrapper(Protocol[F]):
    @property
    def __call__(self) -> F:
        ...


class PDependsOn(Protocol):
    def depends_on(self, *args, **kwargs) -> None:
        ...
