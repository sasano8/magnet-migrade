# type: ignore
import asyncio
import inspect

from pydantic import BaseModel

from framework.analyzers import AnyAnalyzer, FuncAnalyzer

####################################################################
# AnyAnalyzer
####################################################################


# def test_get_annotations():
#     class A:
#         name: str

#         def hello(self):
#             return "a"

#     class B:
#         age: int

#         def hello(self):
#             return "b"

#     class C(A, B):
#         ...

#     class D(BaseModel):
#         name: str

#     class E(BaseModel):
#         age: int

#     class F(D, E):
#         sex: float

#     def func(name: str):
#         ...

#     if obj := C:
#         assert obj.__annotations__ == {"name": str}
#         annotations = AnyAnalyzer.get_annotations(obj)
#         assert annotations == {"name": str, "age": int}

#     if obj := F:
#         assert obj.__annotations__ == {"sex": float}
#         annotations = AnyAnalyzer.get_annotations(obj)
#         assert annotations == {"name": str, "age": int, "sex": float}

#     if obj := func:
#         assert obj.__annotations__ == {"name": str}
#         annotations = AnyAnalyzer.get_annotations(obj)
#         assert annotations == {"name": str}


def test_get_type_hints():
    class A:
        name: str

        def hello(self):
            return "a"

    class B:
        age: int

        def hello(self):
            return "b"

    class C(A, B):
        ...

    class D(BaseModel):
        name: str

    class E(BaseModel):
        age: int

    class F(D, E):
        sex: float

    def func(name: str):
        ...

    if obj := C:
        assert obj.__annotations__ == {"name": str}
        annotations = AnyAnalyzer.get_type_hints(obj)
        assert annotations == {"name": str, "age": int}

    if obj := F:
        assert obj.__annotations__ == {"sex": float}
        annotations = AnyAnalyzer.get_type_hints(obj)
        assert annotations == {"name": str, "age": int, "sex": float}

    if obj := func:
        assert obj.__annotations__ == {"name": str}
        annotations = AnyAnalyzer.get_type_hints(obj)
        assert annotations == {"name": str}


def func():
    return 1


async def func_async():
    return 2


class Dummy:
    def method(self):
        pass


####################################################################
# FuncAnalyzer
####################################################################


def test_analyze():
    info = FuncAnalyzer(func)
    assert info.is_function()
    assert not info.is_method()
    assert not info.is_unbounded_method()
    assert not info.is_static_method()

    info = FuncAnalyzer(Dummy.method)
    assert info.is_function()
    assert not info.is_method()  # インスタンスが作成されるまではmethodではない
    assert info.is_unbounded_method()
    assert not info.is_static_method()

    info = FuncAnalyzer(Dummy().method)
    assert not info.is_function()
    assert info.is_method()
    assert not info.is_unbounded_method()
    assert not info.is_static_method()


def test_to_coroutine_callable():
    # 同期関数なら非同期関数でラップした関数を返す
    info = FuncAnalyzer(func)
    wrapped = info.to_coroutine_callable()
    assert inspect.iscoroutinefunction(wrapped)
    assert asyncio.run(wrapped()) == 1

    # すでに非同期関数ならそのまま返す
    info = FuncAnalyzer(func_async)
    wrapped = info.to_coroutine_callable()
    assert wrapped == func_async
    assert inspect.iscoroutinefunction(wrapped)
    assert asyncio.run(wrapped()) == 2


def test_partial():
    def return_str(msg: str):
        """abcd"""
        return msg

    func = FuncAnalyzer(return_str).partial("hello")
    assert func.__name__ == "return_str"
    assert func.__doc__ == "abcd"
    assert func() == "hello"


def test_update_signature():
    def func1(*args, **kwargs):
        pass

    def func2(name, /, age, *, sex):
        pass

    def func3(name="test", /, age=20, *, sex=0) -> int:
        pass

    def func4(name: str = "test", /, age: int = 20, *, sex: int = 0) -> int:
        pass

    # デフォルトの挙動確認
    assert func1.__defaults__ == None
    assert func1.__kwdefaults__ == None
    assert func1.__annotations__ == {}

    assert func2.__defaults__ == None
    assert func2.__kwdefaults__ == None
    assert func2.__annotations__ == {}

    assert func3.__defaults__ == ("test", 20)
    assert func3.__kwdefaults__ == dict(sex=0)
    assert func3.__annotations__ == {"return": int}

    assert func4.__defaults__ == ("test", 20)
    assert func4.__kwdefaults__ == dict(sex=0)
    assert func4.__annotations__ == {"name": str, "age": int, "sex": int, "return": int}

    info = FuncAnalyzer(func1)
    sig = info.get_signature()
    assert list(sig.parameters) == ["args", "kwargs"]

    info.update_signature(FuncAnalyzer.get_signature(func2))
    sig = info.get_signature()
    assert list(sig.parameters) == ["name", "age", "sex"]
    assert func1.__defaults__ == None
    assert func1.__kwdefaults__ == None
    assert func1.__annotations__ == {}

    info.update_signature(FuncAnalyzer.get_signature(func3))
    sig = info.get_signature()
    assert list(sig.parameters) == ["name", "age", "sex"]
    assert func1.__defaults__ == ("test", 20)
    assert func1.__kwdefaults__ == dict(sex=0)
    assert func1.__annotations__ == {"return": int}

    info.update_signature(FuncAnalyzer.get_signature(func4))
    sig = info.get_signature()
    assert list(sig.parameters) == ["name", "age", "sex"]
    assert func1.__defaults__ == ("test", 20)
    assert func1.__kwdefaults__ == dict(sex=0)
    assert func1.__annotations__ == {"name": str, "age": int, "sex": int, "return": int}

    info.update_signature(FuncAnalyzer.get_signature(func4), return_annotation=str)
    assert func1.__annotations__ == {"name": str, "age": int, "sex": int, "return": str}
