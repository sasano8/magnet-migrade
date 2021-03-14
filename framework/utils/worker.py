from __future__ import annotations

import asyncio
import logging
from functools import partial, wraps
from typing import Any, Callable, Coroutine, Iterable, Iterator, List, Tuple, TypeVar

from framework.analyzers import FuncAnalyzer

T = TypeVar("T", bound=Callable)


class Task:
    # TODO: Coroutine functionにする
    def __init__(self, coroutine_callable: Callable[..., Coroutine]) -> None:
        if not FuncAnalyzer.is_coroutine_callable(coroutine_callable):
            raise TypeError(f"{coroutine_callable} is not coroutine_callable")
        self._coroutine_function = coroutine_callable
        self._task: asyncio.Task = None

        self.__name__ = self.get_name_from(coroutine_callable)
        self._result = None
        self._exception = None
        self._cancelled = False
        self._done = False

    @staticmethod
    def get_name_from(obj):
        if isinstance(obj, partial):
            target = obj.func
        else:
            target = obj

        if hasattr(obj, "__name__"):
            return target.__name__
        else:
            return target.__class__.__name__

    def get_name(self):
        if self._task:
            return self._task.get_name()
        return self.__name__

    # @property
    # def name(self):
    #     return self.__name__

    # @name.getter
    # def name(self, value):
    #     return self.__name__

    # @name.setter
    # def name(self, value):
    #     self.__name__ = value

    def result(self):
        if self._task is None:
            raise asyncio.exceptions.InvalidStateError("Result is not set.")
        else:
            return self._task.result()

    # def set_result(self):
    #     return 1

    def exception(self):
        if self._task is None:
            raise asyncio.exceptions.InvalidStateError("Exception is not set.")
        else:
            return self._task.exception()

    # def set_exception(self):
    #     return 1

    def cancel(self):
        if self._task is None:
            raise asyncio.exceptions.InvalidStateError(
                "Can not cancel. Task is not scheduled."
            )
        self._task.cancel()

    def cancelled(self):
        if self._task is None:
            return False
        else:
            return self._task.cancelled()

    def done(self):
        if self._task is None:
            return False
        else:
            return self._task.done()

    def add_done_callback(self, fn: Callable) -> None:
        return self._task.add_done_callback(fn)

    def remove_done_callback(self, fn: Callable) -> int:
        return self._task.remove_done_callback(fn)

    def schedule(self, *args: Any, **kwargs: Any) -> asyncio.Task:
        if self._task is not None:
            raise RuntimeError("Task already run.")
        co = self._coroutine_function(*args, **kwargs)
        self._task = asyncio.create_task(co)
        return self._task

    async def __call__(self, *args: Any, **kwargs: Any):
        return await self.schedule(*args, **kwargs)

    # def set_task(self, future: asyncio.Future):
    #     self._task = future
    #     self._task.set_name(self._task.get_name())


class SupervisorAsync(Iterable[Task]):
    """実行するコルーチン関数を管理する"""

    def __init__(self, coroutine_functions: Iterable[Callable[..., Coroutine]]) -> None:
        self.__root__ = coroutine_functions

    def __iter__(self) -> Iterator[Task]:
        return self.__root__.__iter__()

    # @staticmethod
    # def covert_coroutines_to_tasks(
    #     coroutine_functions: Iterable[Callable[..., Coroutine]]
    # ):
    #     tasks = [Task(x) for x in coroutine_functions]
    #     return tasks

    def to_executor(self, logger=None) -> LinqAsyncExecutor:
        # コルーチンファンクションからコルーチンを生成し、一度のみ実行可能なエクゼキュータを生成する
        # tasks = self.covert_coroutines_to_tasks(self.__root__)
        executor = LinqAsyncExecutor(self.__root__, logger)
        return executor

    def __enter__(self):
        raise NotImplementedError()
        # 実装したい
        # enterとexitは自身に対して呼び出される
        # __enter__で別のオブジェクトをリターンしても、exitが呼ばれるのはこのオブジェクト

    def __exit__(self, ex_type, ex_value, trace):
        raise NotImplementedError()

    def __await__(self):
        raise NotImplementedError()

        async def func():
            await asyncio.sleep(0)

        return func().__await__()


# なにをやる？
# 具体的な処理と管理を記述する
class LinqAsyncExecutor(SupervisorAsync):
    """管理しているコルーチン関数からコルーチンを生成し、その実行管理を行う"""

    def __init__(
        self, coroutine_functions: Iterable[Callable[..., Coroutine]], logger
    ) -> None:
        self.__root__: List[Task] = []
        for cf in coroutine_functions:
            if FuncAnalyzer.is_coroutine_callable(cf):
                self.__root__.append(Task(cf))
            else:
                raise TypeError(f"{cf} is not coroutine function.")

        # self.on_each_complete = None
        self.current_tasks = None
        self.logger = logging.getLogger() if logger is None else logger

    # def set_on_each_complete(self, callback):
    #     self.on_each_complete = callback

    async def __call__(self):
        self.start()

        try:
            while self.completed() == False:
                await asyncio.sleep(1)

        except asyncio.exceptions.TimeoutError as e:
            print("timeout!!!")
        except Exception as e:
            print("exception!!!!")
            raise

    # def __await__(self):
    #     # 完了管理を行うこと
    #     return self().__await__()

    def run(self):
        """タスクを実行し、完了まで待機します。"""
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError as e:
            loop = None

        if loop is None:
            asyncio.run(self.run_async())
        else:
            # asyncioはネストしたイベントループを許可していない。それをハックするのも難しい
            raise RuntimeError(
                "This event loop is already running. use `run_async` insted of"
            )

    async def run_async(self):
        """タスクを実行し、完了まで待機します。"""
        self.start()
        await self.join()

    def start(self):
        """タスクをスケジューリングします。完了まで待機されません。"""
        if self.current_tasks is not None:
            raise RuntimeError("cannot reuse already awaited coroutine")

        self.current_tasks = []
        monitor_tasks = self.current_tasks

        # add_done_callbackのコールバックは即時実行される。実行中タスクが完了する前にメッセージが出力されてしまう。
        def lazy_notify(task):
            async def callback(task):
                await asyncio.sleep(1)
                self.log(task)

            asyncio.create_task(callback(task))

        for task in self:
            future = task.schedule()
            monitor_tasks.append(future)
            future.add_done_callback(monitor_tasks.remove)
            future.add_done_callback(lazy_notify)

    async def stop(self, timeout=10000):
        """タスクをストップし、全てのタスクが完了もしくはキャンセルされるまで待ちます。"""
        if self.current_tasks is None:
            raise Exception("The coroutine has not been executed yet")

        for task in self.current_tasks:
            if not task.done():
                task.cancel()

        await self.join()

    async def join(self):
        """全てのタスクが終了するまで待機します。サーバプログラム等の無限ループ処理は、代わりにstopを利用してください。"""
        while self.is_completed_or_raise() == False:
            await asyncio.sleep(1)

    def is_completed_or_raise(self):
        if self.current_tasks is None:
            raise Exception("The coroutine has not been executed yet")

        return self.completed()

    def completed(self):
        if self.current_tasks is None:
            return False
        else:
            return len(self.current_tasks) == 0

    def log(self, task: asyncio.Task) -> None:
        logger = self.logger
        try:
            task.result()
            logger.info(f"[COMPLETE]{task}")
            # print(f"{task}[COMPLETE]")
        except asyncio.CancelledError:
            logger.info(f"[CANCEL]{task}")
        except Exception:  # pylint: disable=broad-except
            # logger.exception(message, *message_args)
            import traceback

            logger.warning(traceback.format_exc())
            logger.warning(f"[FAILED]{task}")

    # 実装しない。それとも、loopを管理して、終了させるか。それはちょっとめんどい
    # def __del__(self):
    #     raise NotImplementedError()
    # def to_executor(self):
    #     # 継承すべきではない
    #     raise NotImplementedError()

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, ex_type, ex_value, trace):
        raise NotImplementedError()

    async def __aenter__(self):
        raise NotImplementedError()
        await self.start()

    async def __aexit__(self, ex_type, ex_value, trace):
        raise NotImplementedError()
        await self.stop()
