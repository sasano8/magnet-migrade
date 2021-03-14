from __future__ import with_statement

import asyncio
from asyncio.events import get_running_loop
from functools import partial
from typing import Iterable

import pytest

from framework import Linq


def test_default_coroutine_behavior():
    async def func():
        yield 1

    async def main():
        async for x in func():
            assert x == 1

    asyncio.run(main())


def test_default_future_behavior():
    async def get_future_result():
        future = asyncio.create_task(asyncio.sleep(0.1))

        assert not future.done()
        assert not future.cancelled()
        with pytest.raises(
            asyncio.exceptions.InvalidStateError, match="Exception is not set."
        ):
            future.exception()
        with pytest.raises(
            asyncio.exceptions.InvalidStateError, match="Result is not set."
        ):
            future.result()

        await future

        assert future.done()
        assert not future.cancelled()
        assert future.result() is None
        assert future.exception() is None

    asyncio.run(get_future_result())


async def func1():
    await asyncio.sleep(0.2)
    return 1


async def func2():
    await asyncio.sleep(0.1)
    return 2


async def func3():
    return 3


def test_async_run():

    results = Linq.asyncio([func1, func2, func3]).run()
    assert results == [1, 2, 3]  # 完了順でなく、引数に渡したコルーチン順で結果が返る


@pytest.mark.filterwarnings("ignore::RuntimeWarning")  # coroutine was never awaited
def test_async_run_in_event_loop():
    async def main():
        results = Linq.asyncio([func1, func2, func3]).run()
        assert results == [1, 2, 3]

    with pytest.raises(
        RuntimeError,
        match="not be called from a running event loop. Use `gather` instead of `run`",
    ):
        asyncio.run(main())


def test_async_gather_in_event_loop():
    async def main():
        results = await Linq.asyncio([func1, func2, func3]).gather()
        assert results == [1, 2, 3]

    asyncio.run(main())


def test_async_gather_from_asyncio_run():
    main = Linq.asyncio([func1, func2, func3]).gather()
    results = asyncio.run(main)
    assert results == [1, 2, 3]


def test_async_iterable_one_elm():
    async def main():
        async_iterable = Linq.asyncio([func1])

        async for x in async_iterable:
            assert x == 1

    asyncio.run(main())


def test_async_iterable_three_elm():
    async def main():
        async_iterable = Linq.asyncio([func1, func2, func3])

        count = 0
        async for x in async_iterable:
            count += 1
            assert x == count

    asyncio.run(main())


def test_supervise_task():
    async_iterable = Linq.asyncio([func1])
    supervisor = async_iterable.supervise().to_executor()

    for task in supervisor:
        print(task)
        assert not task.done()


def test_supervise_start_stop_cancel():
    import functools

    result = False

    async def func(wait):
        await asyncio.sleep(wait)
        nonlocal result
        result = True
        return True

    async_iterable = Linq.asyncio([functools.partial(func, 1)])
    supervisor = async_iterable.supervise().to_executor()

    async def main():
        assert [task.done() for task in supervisor] == [False]
        assert not supervisor.completed()

        supervisor.start()

        assert [task.done() for task in supervisor] == [False]
        assert not supervisor.completed()

        await supervisor.stop()

        assert [task.done() for task in supervisor] == [True]
        assert supervisor.completed()

        with pytest.raises(
            RuntimeError, match="cannot reuse already awaited coroutine"
        ):
            supervisor.start()

    asyncio.run(main())

    for task in supervisor:
        assert task.done()
        assert task.cancelled()

        with pytest.raises(asyncio.exceptions.CancelledError):
            task.exception()

        with pytest.raises(asyncio.exceptions.CancelledError):
            task.result()

    assert not result


def test_supervise_start_stop_complete():
    import functools

    result = False

    async def func(wait):
        await asyncio.sleep(wait)
        nonlocal result
        result = True
        return True

    async_iterable = Linq.asyncio([functools.partial(func, 1)])
    supervisor = async_iterable.supervise().to_executor()

    async def main():
        assert [task.done() for task in supervisor] == [False]
        assert not supervisor.completed()

        supervisor.start()

        assert [task.done() for task in supervisor] == [False]
        assert not supervisor.completed()

        # await supervisor.stop()
        await asyncio.sleep(2)

        assert [task.done() for task in supervisor] == [True]
        assert supervisor.completed()

        with pytest.raises(
            RuntimeError, match="cannot reuse already awaited coroutine"
        ):
            supervisor.start()

    asyncio.run(main())

    for task in supervisor:
        assert task.done()
        assert not task.cancelled()
        assert task.exception() is None
        assert task.result()

    assert result
