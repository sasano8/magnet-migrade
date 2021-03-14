from __future__ import annotations

import asyncio
from typing import Any, Callable, Coroutine, Generic, TypeVar, cast

from pp import FuncMimicry, FuncWrapper
from pp.protocols import PFuncWrapper

from .analyzer_func import FuncAnalyzer

F = TypeVar("F", bound=Callable)


class RecursiveFunctionAsync(FuncWrapper[F]):
    """関数が返される限り、関数を実行し続ける、再帰的関数のビルダー。
    1. コンストラクタに状態初期化関数を渡す。
    2. on_mainイベントにエントリポイント関数を設定する
    3. 関数が帰れば、その関数を再帰実行。それ以外なら終了
    """

    def __init__(self, __root__: F):
        self.__root__ = __root__
        self.events = self.create_default_events()
        self.events["on_init"] = __root__

    @staticmethod
    def create_default_events():
        return dict(
            on_cancel=lambda state: None,
            on_init=None,
            on_main=None,
            on_success=lambda state: None,
            on_error=lambda state: None,
            on_complete=lambda state: None,
            on_next=lambda staet: None,
        )

    def set_logger(self, logger=None):
        import logging

        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        # handler = logging.StreamHandler()
        # handler.setLevel(logging.INFO)
        # logger.addHandler(handler)
        self.logger = logger

    def on_cancel(self, func):
        self.events["on_cancel"] = func
        return func

    def on_init(self, func):
        self.events["on_init"] = func
        return func

    def on_main(self, func):
        self.events["on_main"] = func
        return func

    # not implemented
    def on_success(self, func):
        self.events["on_success"] = func
        return func

    # not implemented
    def on_error(self, func):
        self.events["on_error"] = func
        return func

    # not implemented
    def on_complete(self, func):
        self.events["on_complete"] = func
        return func

    # not implemented
    def on_next(self, func):
        self.events["on_next"] = func
        return func

    # not implemented
    def on_step(self, func):
        return func

    @property
    def __call__(self) -> F:
        return self.__call  # type: ignore

    async def __call(self, *args, **kwargs):
        async for state in self.__aiter__(*args, **kwargs):
            ...

    async def __aiter__(self, *args, **kwargs):
        async for state in self.resume(*args, **kwargs):
            yield state

    async def resume(self, *args, **kwargs):
        print("# 例外が発生した場合、何も出力されない！！")
        self.set_logger()  # TODO: ちゃんと実装する
        logger = self.logger
        on_init = self.events["on_init"]
        on_main = self.events["on_main"]
        on_success = self.events["on_success"]
        on_error = self.events["on_error"]
        on_complete = self.events["on_complete"]
        on_cancel = self.events["on_cancel"]
        on_next = self.events["on_next"]

        state = await on_init(*args, **kwargs)

        if on_main is None:
            raise RuntimeError("No return next function from main.")

        current_func = on_main
        yield state
        while current_func:
            coroutine_function = FuncAnalyzer.to_coroutine_callable(current_func)

            result = None
            task = coroutine_function(state)
            task = asyncio.shield(task)
            while not task.done():
                logger.info(f"[START]{coroutine_function.__name__}")

                try:
                    result = await task
                except (asyncio.CancelledError, KeyboardInterrupt) as e:
                    logger.warning(f"[REQUESTED CANCEL]{coroutine_function.__name__}")
                    state.is_cancelled = True
                    on_cancel(state)  # キャンセルが要求されたら、キャンセルせずにキャンセルメソッドの実装に任せ、完了を待つ
                    continue
                except Exception as e:
                    logger.critical(e, exc_info=True)
                    task.set_exception(e)
                    result = on_error(e)

            if FuncAnalyzer.is_callable(result):
                current_func = result
            else:
                current_func = None

            if task.cancelled():
                msg = "CANCELED"
            else:
                msg = "SUCCESS"

            logger.info(f"[{msg}]{coroutine_function.__name__}")
            yield state
