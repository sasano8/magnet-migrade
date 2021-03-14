import inspect
from functools import partial
from typing import Callable, Type, cast

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel

from .normalizers import Adapters, Unpack, Unpackers
from .signaturebuilder import SignatureBuilder


def get_func_and_update_basemodel_call(func_or_basemodel) -> Callable:
    if inspect.isfunction(func_or_basemodel):
        return func_or_basemodel
    elif issubclass(func_or_basemodel, BaseModel):
        # クラスは暗黙的な__call__を必ず？実装している。
        # ユーザー定義の場合、__module__の存在でチェックができる
        if not hasattr(func_or_basemodel.__call__, "__module__"):
            raise AttributeError(
                f"'{func_or_basemodel.__name__}' object has no attribute '__call__'"
            )

        # TODO: 元のオブジェクトを勝手に触るのは好ましくないのでオーバーライドする方法を考える
        func: Callable = func_or_basemodel.__call__
        func.__annotations__["self"] = func_or_basemodel
        func.__name__ = func_or_basemodel.__name__
        return func
    else:
        raise Exception()


def create_decorator(deco, func_or_basemodel):
    if inspect.isfunction(func_or_basemodel) or not issubclass(
        func_or_basemodel, BaseModel
    ):
        sb = SignatureBuilder.from_func(func_or_basemodel).unpack(
            Unpackers.filter_fastapi
        )
        new_func = sb.get_func(Adapters.to_fastapi)
        # print(new_func.__signature__)
        new_func = deco(new_func)
        return func_or_basemodel
    else:
        func = get_func_and_update_basemodel_call(func_or_basemodel)
        sb = SignatureBuilder.from_func(func).unpack(Unpackers.filter_fastapi)
        new_func = sb.get_func(Adapters.to_fastapi)
        # print(new_func.__signature__)
        deco(new_func)
        return func_or_basemodel


# TODO: デコレータを使用すると遅延評価がほぼ不可能
# パーティアルなので、フレームを＋１するばいけるのか、、、


def assert_future_annotations():
    """前方参照使うと型解析がただしく動かないので禁止"""
    root = inspect.currentframe()
    current = root.f_back.f_back
    g = current.f_globals  # type: ignore
    if annotation := g.get("annotations", None):
        file = g.get("__file__", "")
        raise RuntimeError(f"{file} : Cant use from __future__ import annotations")


class PandemicAPIRouter(APIRouter):
    def get(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().get(*args, **kwargs)
        return partial(create_decorator, deco)

    def put(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().put(*args, **kwargs)
        return partial(create_decorator, deco)

    def post(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().post(*args, **kwargs)
        return partial(create_decorator, deco)

    def delete(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().delete(*args, **kwargs)
        return partial(create_decorator, deco)

    def options(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().options(*args, **kwargs)
        return partial(create_decorator, deco)

    def head(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().head(*args, **kwargs)
        return partial(create_decorator, deco)

    def patch(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().patch(*args, **kwargs)
        return partial(create_decorator, deco)

    def trace(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().trace(*args, **kwargs)
        return partial(create_decorator, deco)


class PandemicFastAPI(FastAPI):
    """pydantic based viewを提供する。get時は引数をunpackする。"""

    def get(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().get(*args, **kwargs)
        return partial(create_decorator, deco)

    def put(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().put(*args, **kwargs)
        return partial(create_decorator, deco)

    def post(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().post(*args, **kwargs)
        return partial(create_decorator, deco)

    def delete(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().delete(*args, **kwargs)
        return partial(create_decorator, deco)

    def options(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().options(*args, **kwargs)
        return partial(create_decorator, deco)

    def head(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().head(*args, **kwargs)
        return partial(create_decorator, deco)

    def patch(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().patch(*args, **kwargs)
        return partial(create_decorator, deco)

    def trace(self, *args, **kwargs) -> staticmethod:
        assert_future_annotations()
        deco = super().trace(*args, **kwargs)
        return partial(create_decorator, deco)


create_fastapi = cast(Type[FastAPI], PandemicFastAPI)
create_router = cast(Type[APIRouter], PandemicAPIRouter)
