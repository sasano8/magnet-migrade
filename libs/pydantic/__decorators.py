import asyncio
import functools
from inspect import signature

from pydantic import BaseModel

from framework.analyzers import FuncAnalyzer as FA

from .utils import generate_fastapi_funnel, generate_typer_funnel


# TODO: 作りが微妙なので整理する
class FuncAnalyer:
    def __init__(self, func) -> None:
        self.func = func

        info = FA(func)
        sig = info.get_signature()

        # TODO: callableでもいいかも
        if not info.is_function():
            raise TypeError(f"{func.__name__} is not function.")

        self.signature = list(sig.parameters.items())
        self.is_method = info.is_method() or info.is_unbounded_method()
        self.is_coroutine_function = info.is_coroutine_callable()

        self._valid(self.is_method)

    def _valid(self, is_method_or_unbounded_method):
        if is_method_or_unbounded_method:
            self.signature.pop(0)  # cls, selfを除外する

        args_len = len(self.signature)
        if args_len != 1:
            raise TypeError(f"{self.func.__name__}: 単一の引数にBaseModelを持つ関数でありません。")
        key, param = self.signature[0]
        if not issubclass(param.annotation, BaseModel):
            raise TypeError(f"{self.func.__name__} {key}: BaseModelを継承したクラスでありません。")

    def get_base_model_class(self):
        key, param = self.signature[0]
        return param.annotation

    def filter_depends_security(self):
        raise NotImplementedError()


def fastapi_funnel(func):
    """
    単一のBaseModel引数を持つ関数・メソッドをfastapiのクエリとして解釈するための関数・メソッドを定義します。
    関数・メソッドは以下のように解釈されます。

    class MyClass(BaseModel):
      name: str
      age: int = Field(alias="generation")

    @model_overload_for_api
    def func(obj: MyClass):
      pass

    ↓

    def wapped(name: str = Query(alias="name"), age: int = Query(alias="generation")):
      func(MyClass(
        name=name,
        age=age
      ))
    """
    analyzer = FuncAnalyer(func)
    is_method = analyzer.is_method
    is_coroutine_function = analyzer.is_coroutine_function
    base_model = analyzer.get_base_model_class()

    # ここまで共通処理

    instantiate_model = generate_fastapi_funnel(cls=base_model, as_method=is_method)

    if is_method:

        @functools.wraps(instantiate_model)
        def wrapper(*args, **kwargs):
            if len(args):
                self_or_cls = args[0]
            else:
                # XXX: fastapiかfastapi-utilsのせいかなぜかキーワードにselfが渡ってくる
                self_or_cls = kwargs.pop("self", None)
                if self_or_cls is None:
                    self_or_cls = kwargs.pop("cls", None)

            model = instantiate_model(self_or_cls, **kwargs)
            return func(self_or_cls, model)

    else:

        @functools.wraps(instantiate_model)
        def wrapper(*args, **kwargs):
            model = instantiate_model(**kwargs)
            return func(model)

    if is_coroutine_function:
        origin_wrapper = wrapper

        @functools.wraps(origin_wrapper)
        async def wrapper(*args, **kwargs):
            return await origin_wrapper(*args, **kwargs)

    wrapper.interface = wrapper  # type: ignore
    wrapper.origin = func  # type: ignore
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__qualname__ = func.__qualname__
    if "return" in func.__annotations__:
        wrapper.__annotations__["return"] = func.__annotations__["return"]

    return wrapper


def typer_funnel(func=None, **kwargs):
    """
    単一のBaseModel引数を持つ関数・メソッドをfastapiのクエリとして解釈するための関数・メソッドを定義します。
    関数・メソッドは以下のように解釈されます。

    class MyClass(BaseModel):
      name: str
      age: int = Field(alias="generation")

    @model_overload_for_api
    def func(obj: MyClass):
      pass

    ↓

    def wapped(name: str = Query(alias="name"), age: int = Query(alias="generation")):
      func(MyClass(
        name=name,
        age=age
      ))
    """
    if not callable(func):
        return functools.partial(typer_funnel, **kwargs)

    analyzer = FuncAnalyer(func)
    is_method = analyzer.is_method
    is_coroutine_function = analyzer.is_coroutine_function
    base_model = analyzer.get_base_model_class()

    # ここまで共通処理

    instantiate_model = generate_typer_funnel(
        cls=base_model, as_method=is_method, options=kwargs
    )

    if is_method:

        @functools.wraps(instantiate_model)
        def wrapper(*args, **kwargs):
            if len(args):
                self_or_cls = args[0]
            else:
                # XXX: fastapiかfastapi-utilsのせいかなぜかキーワードにselfが渡ってくる
                self_or_cls = kwargs.pop("self", None)
                if self_or_cls is None:
                    self_or_cls = kwargs.pop("cls", None)

            model = instantiate_model(self_or_cls, **kwargs)
            return func(self_or_cls, model)

    else:

        @functools.wraps(instantiate_model)
        def wrapper(*args, **kwargs):
            model = instantiate_model(**kwargs)
            return func(model)

    if is_coroutine_function:
        origin_wrapper = wrapper

        @functools.wraps(origin_wrapper)
        async def wrapper(*args, **kwargs):
            return await origin_wrapper(*args, **kwargs)

    wrapper.interface = wrapper  # type: ignore
    wrapper.origin = func  # type: ignore
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__qualname__ = func.__qualname__
    if "return" in func.__annotations__:
        wrapper.__annotations__["return"] = func.__annotations__["return"]

    return wrapper


pydantic_sig_to_typer_sig = typer_funnel


def funnel(func):
    analyzer = FuncAnalyer(func)
    is_method = analyzer.is_method
    is_coroutine_function = analyzer.is_coroutine_function
    base_model = analyzer.get_base_model_class()

    # ここまで共通処理

    instantiate_model = base_model

    if is_method:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 1:
                args = tuple([args[0], instantiate_model(**kwargs)])
            else:
                if len(kwargs):
                    raise ValueError("位置限定引数とキーワード限定引数のいずれかのみ受け入れ可能です。")
            return func(*args)

    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if len(args) == 0:
                args = tuple([instantiate_model(**kwargs)])
            else:
                if len(kwargs):
                    raise ValueError("位置限定引数とキーワード限定引数のいずれかのみ受け入れ可能です。")
            return func(*args)

    if is_coroutine_function:
        origin_wrapper = wrapper

        @functools.wraps(origin_wrapper)
        async def wrapper(*args, **kwargs):
            return await origin_wrapper(*args, **kwargs)

    return wrapper
