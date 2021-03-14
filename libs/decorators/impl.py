from libs.decorators import abstract
from typing import Callable
from inspect import signature
import json
import asyncio
from functools import wraps, partial
from pydantic import parse_obj_as, Json

"""
デコレータパターン

wrap
    - pre processing
    - post processing 

mimic
    - instantiate

constractor: 定義時の初期化処理を
tag: オブジェクトにタグを追加する

"""

class Instantiate(abstract.InterfaceDecorator):
    """クラスに付与することで、クラス宣言時にそのクラスのインスタンスを作成し、クラスをインスタンスに置き換える。"""
    def valid_target(self, target):
        return isinstance(target, type)

    def return_decorated(self, target):
        obj = target(*self.args, **self.kwargs)
        return obj


class Hook(abstract.InterfaceDecorator):
    """対象の宣言時にフック処理を注入する。"""
    def __init__(self, *, func):
        self.hook_func = func

    def valid_target(self, target):
        return True

    def return_decorated(self, target):
        return target

    def hook(self, target):
        self.hook_func(target)


class Extension(abstract.InterfaceDecorator):
    """対象の宣言時にフック処理を注入する。"""
    def __init__(self, *, target, name=None, override=False):
        self.target = target
        self.extension_name = name
        self.override = override

    def valid_target(self, target):
        return True

    def return_decorated(self, target):
        return target

    def hook(self, target):
        if not self.extension_name:
            self.extension_name = target.__name__

        if hasattr(self.target, self.extension_name):
            if not self.override:
                raise ValueError("属性がすでに存在します。: {} {}".format(self.target, self.extension_name))

        setattr(target, self.extension_name, self.extension)


class PrintLog(abstract.FuncDecorator):
    def __init__(self):
        pass

    def wrapper(self, func, *args, **kwargs):
        print("[START]{}".format(func))
        obj = func(*args, **kwargs)
        print("[END]{}".format(func))
        return obj


class Tag(abstract.InterfaceDecorator):
    def __init__(self, tag: str = "default", key_selector: Callable = lambda x: x):
        self.tag = tag

        from libs.decorators import repository
        self.rep = repository.Repoisotry(name=tag, key_selector=key_selector)

    def valid_target(self, target):
        return True

    def return_decorated(self, target):
        return target

    def hook(self, target):
        self.append(target)

    def list(self):
        for key, value in self.rep.list():
            yield key, value

    def append(self, obj):
        return self.rep.append(obj)
    
    def get(self, key):
        return self.rep.get(key)

    def update(self, obj):
        return self.rep.update(obj)

    def exists(self, key):
        return self.rep.exists(key)


class AsyncOrNormalFuncDecorator(abstract.FuncDecorator):
    def return_decorated(self, func):
        """self.wrapperでラップされた関数を返す。"""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def wrapped(*args, **kwargs):
                return await self.wrapper_async(func, *args, **kwargs)
        else:
            @wraps(func)
            def wrapped(*args, **kwargs):
                return self.wrapper(func, *args, **kwargs)
        return wrapped

    def wrapper(self, func, *args, **kwargs):
        pass

    async def wrapper_async(self, func, *args, **kwargs):
        pass

class Decode(AsyncOrNormalFuncDecorator):
    """JSON文字列を戻り値とする関数・メソッドのデコレータ。JSON文字列を、タイプヒントの戻り値の型に変換する。"""
    def wrapper(self, func, *args, **kwargs):
        json_text = func(*args, **kwargs)
        dic = json.loads(json_text)
        return dic

    async def wrapper_async(self, func, *args, **kwargs):
        json_text = await func(*args, **kwargs)
        dic = json.loads(json_text)
        return dic


class MapDict(AsyncOrNormalFuncDecorator):
    """辞書を戻り値とする関数・メソッドのデコレータ。辞書を、タイプヒントの戻り値の型に変換する。"""
    # def __init__(self, pydantic_cls):
    #     self.pydantic_cls = pydantic_cls
    #
    # def require_init(self):
    #     return True

    def init_target(self, target):
        sig = signature(target)
        self.return_type = sig.return_annotation

    def wrapper(self, func, *args, **kwargs):
        dic = func(*args, **kwargs)
        # obj = self.return_type(**dic)
        obj = parse_obj_as(self.return_type, dic)
        return obj

    async def wrapper_async(self, func, *args, **kwargs):
        dic = await func(*args, **kwargs)
        # obj = self.return_type(**dic)
        obj = parse_obj_as(self.return_type, dic)
        return obj


class MapJson(AsyncOrNormalFuncDecorator):
    """JSON文字列を戻り値とする関数・メソッドのデコレータ。JSON文字列を、タイプヒントの戻り値の型に変換する。"""
    def init_target(self, target):
        sig = signature(target)
        self.return_type = sig.return_annotation

    def wrapper(self, func, *args, **kwargs):
        json_text = func(*args, **kwargs)
        # dic = json.loads(json_text)
        # obj = self.return_type(**dic)
        obj = parse_obj_as(Json[self.return_type], json_text)
        return obj

    async def wrapper_async(self, func, *args, **kwargs):
        json_text = await func(*args, **kwargs)
        # dic = json.loads(json_text)
        # obj = self.return_type(**dic)
        obj = parse_obj_as(Json[self.return_type], json_text)
        return obj



