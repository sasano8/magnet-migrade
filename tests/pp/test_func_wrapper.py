import asyncio
import inspect

from pp import FuncMimicry


class FuncMimicry2(FuncMimicry):
    ...


def func_no_args():
    pass


def func_args(name: str):
    pass


def func_kwargs(name: str = ""):
    pass


def func_return_one():
    return 1


async def func_async_return_two():
    return 2


attr_tests = [func_no_args, func_args, func_kwargs]
async_or_normal_tests = [func_return_one, func_async_return_two]


def test_attributes():
    def assert_func(func, factory):
        wrapper = factory(func)

        for attr_name in {
            "__code__",
            "__doc__",
            "__qualname__",
            "__defaults__",
            "__kwdefaults__",
            "__annotations__",
            "__name__",
            "__class__",
            "__module__",
        }:
            assert getattr(func, attr_name) == getattr(wrapper, attr_name)
            assert func.__dict__ != wrapper.__dict__

        assert wrapper.__wrapped__ == func

    [assert_func(func, FuncMimicry) for func in attr_tests]
    [assert_func(func, FuncMimicry2) for func in attr_tests]


def test_inspect():

    same_checkers = [
        callable,
        inspect.isbuiltin,
        inspect.isabstract,
        inspect.isasyncgen,
        inspect.isasyncgenfunction,
        inspect.isawaitable,
        inspect.isclass,
        inspect.iscode,
        inspect.iscoroutine,
        inspect.iscoroutinefunction,
        inspect.isfunction,
        inspect.isdatadescriptor,
        inspect.isframe,
        inspect.isgenerator,
        inspect.isgeneratorfunction,
        inspect.isgetsetdescriptor,
        inspect.ismemberdescriptor,
        inspect.ismethod,
        inspect.ismodule,
        inspect.istraceback,
    ]

    def assert_func(func, factory):
        wrapper = factory(func)
        for check in same_checkers:
            assert check(func) == check(wrapper)

        if inspect.iscoroutinefunction(func):
            assert asyncio.run(func()) == asyncio.run(wrapper())
        else:
            assert func() == wrapper()

    [assert_func(func, FuncMimicry) for func in async_or_normal_tests]
    [assert_func(func, FuncMimicry2) for func in async_or_normal_tests]


def test_type_check():
    wrapper = FuncMimicry(func_return_one)
    assert wrapper.__class__.__name__ == "function"
    assert type(wrapper) is FuncMimicry
