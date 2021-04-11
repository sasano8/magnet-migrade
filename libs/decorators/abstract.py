from functools import wraps, partial
import inspect
import asyncio
from pydantic import BaseModel, Extra


class InterfaceDecorator:
    def __new__(cls, *args, **kwargs):

        self = super().__new__(cls)
        self.args = ()
        self.kwargs = {}

        if self.require_init():
            self.args = args
            self.kwargs = kwargs
            # self.__init__(*self.args, **self.kwargs) # なぜかreturn後に勝手に呼ばれる
            return self

        is_target = self.is_target(*args, **kwargs)

        # 引数が省略あるいはキーワード引数が渡された場合
        # 例１
        # @deco()
        # def func()
        #
        # 例２
        # deco(name="test")
        # def func()
        if not is_target:
            self.args = args
            self.kwargs = kwargs
            # self.__init__(*self.args, **self.kwargs) # なぜかreturn後に勝手に呼ばれる
            return self

        # 位置引数が一つ　かつ　それが想定している型の場合は、即デコレータを実行する（括弧省略時）
        # 例１
        # @deco
        # def func()
        #
        # 例２
        # deco(func)
        else:
            # returnしない場合なぜかinitは呼ばれないので、手動で呼び出す。
            self.__init__()
            target = args[0]
            obj = self.__call__(target)
            return obj

    def __init__(self, *args, **kwargs):
        pass

    def require_init(self):
        return False

    def is_target(self, *args, **kwargs):
        # 一つの引数　かつ　基本的に関数を想定している
        if len(args) == 1 and len(kwargs) == 0:
            if not self.valid_target(args[0]):
                raise ValueError("想定していない型が引数に渡されました。:{}".format(args[0]))
            else:
                return True
        else:
            return False

    # def __call__(self, *args, **kwargs):
    def __call__(self, target):
        if not self.valid_target(target):
            raise ValueError("想定していない型が引数に渡されました。:{}".format(target))

        self.init_target(target)
        wrapped = self.return_decorated(target)
        self.hook(wrapped)
        return wrapped

    def valid_target(self, target):
        raise NotImplementedError()

    def return_decorated(self, target):
        """デコレートされたオブジェクト、あるいは、対象の情報から生成された別のオブジェクトを返す。"""
        raise NotImplementedError()

    def hook(self, target):
        """対象デコレート後に処理をフックする。"""
        pass

    def init_target(self, target):
        pass


class FuncDecorator(InterfaceDecorator):
    """wrapperをオーバーライドすることで、ラップされた関数を提供する。"""

    def valid_target(self, target):
        return callable(target)

    def return_decorated(self, func):
        """self.wrapperでラップされた関数を返す。"""
        if asyncio.iscoroutinefunction(func):
            if asyncio.iscoroutinefunction(self.wrapper):

                @wraps(func)
                async def wrapped(*args, **kwargs):
                    return await self.wrapper(func, *args, **kwargs)

            else:

                @wraps(func)
                async def wrapped(*args, **kwargs):
                    return self.wrapper(func, *args, **kwargs)

        else:
            # @wraps(func)
            # def wrapped(*args, **kwargs):
            #     return self.wrapper(func, *args, **kwargs)
            if asyncio.iscoroutinefunction(self.wrapper):
                # @wraps(func)
                # async def wrapped(*args, **kwargs):
                #     return await self.wrapper(func, *args, **kwargs)
                raise Exception("asyncでない関数をasync関数でラップすることはライブラリの仕様上禁止しています。")
            else:

                @wraps(func)
                def wrapped(*args, **kwargs):
                    return self.wrapper(func, *args, **kwargs)

        # if inspect.ismethod(func):
        #     return wraps(func)(partial(self.wrapper, func))
        #
        # else:
        #     return wraps(func)(partial(self.wrapper, func=func))
        return wrapped

    def wrapper(self, func, *args, **kwargs):
        return func(*args, **kwargs)
