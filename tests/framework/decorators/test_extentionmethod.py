# type: ignore
from functools import partial

import pytest

from framework.decorators import extensionmethod


def test_platform_behavior():
    class A:
        def hello(self):
            print(self)

        @staticmethod
        def goodbye(self):
            print(self)

    assert list(A.__dict__) == [
        "__module__",
        "hello",
        "goodbye",
        "__dict__",
        "__weakref__",
        "__doc__",
    ]

    defaults = {"__module__", "__dict__", "__weakref__", "__doc__"}

    functions = [x for x in A.__dict__ if x not in defaults]
    assert functions == ["hello", "goodbye"]


def test_emurate_staticmethod():
    class StaticMethod:
        "Emulate PyStaticMethod_Type() in Objects/funcobject.c"

        def __init__(self, f):
            self.f = f

        def __get__(self, obj, objtype=None):
            return self.f

    class A:
        @StaticMethod
        def return_ten():
            return 10

    assert A.return_ten() == 10
    assert A().return_ten() == 10


def test_emurate_method():
    from types import MethodType

    class Method:
        def __init__(self, f):
            self.f = f

        def __get__(self, obj, objtype=None):
            "Simulate func_descr_get() in Objects/funcobject.c"
            if obj is None:
                return self.f
            return MethodType(self.f, obj)

    class A:
        @Method
        def return_self(self):
            return self

    assert A.return_self(10) == 10
    assert isinstance(A().return_self(), A)


def test_emurate_extensionmethod():
    from dataclasses import dataclass
    from functools import wraps
    from types import MethodType

    class ExtensionMethod:
        @classmethod
        def instantiate(cls, func, bind: str = "__root__"):
            self = cls(func=func, bind=bind)
            return wraps(func)(self)

        def __init__(self, func, bind: str = "__root__"):
            self.__func__ = func
            self.__root__ = "__root__"

        def __get__(self, obj, objtype=None):
            if obj is None:
                return self.__func__
            func = self.__func__
            __root__ = self.__root__

            @wraps(func)
            def wrapper(self, *args, **kwargs):
                return func(getattr(self, __root__), *args, **kwargs)

            return MethodType(wrapper, obj)

        def __call__(self, __root__, *args, **kwargs):
            return self.__func__(__root__, *args, **kwargs)

    @dataclass
    class A:
        __root__: str

        @ExtensionMethod.instantiate
        def return_self(self):
            return self

        @ExtensionMethod.instantiate
        def return_name(self, name: str):
            return name

    assert A.return_self(10) == 10
    assert A("value1").return_self() == "value1"
    assert A(__root__="value2").return_self() == "value2"

    from inspect import signature

    assert list(signature(A.return_self).parameters) == ["self"]
    assert list(signature(A(__root__="").return_self).parameters) == []

    assert list(signature(A.return_name).parameters) == ["self", "name"]
    assert list(signature(A(__root__="").return_name).parameters) == ["name"]


def test_atomic_result_staticmethod_and_method():
    # @extension
    class A:
        __root__ = 0

        @extensionmethod
        def add_one(self):
            return self + 1

    obj = A()
    obj.__root__ = 1

    assert A.add_one(0) == 1
    assert obj.add_one() == 2

    # クラスの変数を変更しても、単なるスターティックメソッドとして振る舞うこと
    A.__root__ = 1
    assert A.add_one(0) == 1
    assert A.add_one(1) == 2


def test_extension_with_dataclass():
    from dataclasses import dataclass

    # @extension
    @dataclass
    class TestExtension:
        __root__: str = "test"

        @extensionmethod
        def is_extensionmethod(self):
            return self + "_" + "is_extensionmethod"

    obj = TestExtension()
    assert obj.is_extensionmethod() == "test_is_extensionmethod"

    @dataclass
    class TestExtension2:
        __root__: str = "test"

        @extensionmethod
        def is_extensionmethod(self: str):
            return self + "_" + "is_extensionmethod"

    print(TestExtension2)
    obj2 = TestExtension2()
    assert obj2.is_extensionmethod() == "test_is_extensionmethod"


def test_extension():
    class TestExtension:
        __root__ = "test"

        @extensionmethod
        def is_extensionmethod(self: str):
            return self + "_" + "is_extensionmethod"

        @staticmethod
        def is_staticmethod(self):
            return self + "_" + "is_staticmethod"

        @classmethod
        def is_classmethod(cls):
            return "test" + "_" + "is_classmethod"

    obj = TestExtension()

    pattern = [
        # class + no arg
        (TypeError, TestExtension.is_extensionmethod),
        ("test_is_extensionmethod", partial(TestExtension.is_extensionmethod, "test")),
        ("test_is_extensionmethod", partial(obj.is_extensionmethod)),
        (TypeError, partial(obj.is_extensionmethod, "test")),
        (TypeError, partial(TestExtension.is_staticmethod)),
        ("test_is_staticmethod", partial(TestExtension.is_staticmethod, "test")),
        (TypeError, partial(obj.is_staticmethod)),
        ("test_is_staticmethod", partial(obj.is_staticmethod, "test")),
        ("test_is_classmethod", partial(TestExtension.is_classmethod)),
        (TypeError, partial(TestExtension.is_classmethod, "test")),
        ("test_is_classmethod", partial(obj.is_classmethod)),
        (TypeError, partial(obj.is_classmethod, "test")),
    ]

    def assert_func(index, expected, func):
        if isinstance(expected, type) and issubclass(expected, Exception):
            with pytest.raises(expected):
                func()
        else:
            assert func() == expected

    counter = 0
    for expected, func in pattern:
        counter += 1
        assert_func(counter, expected, func)


def test_todo():
    assert True
    # - extensionの一覧をクラスから取得する仕組みがあるとよい

    # class A:
    #     def func1(self):
    #         ...

    #     def func2(self):
    #         ...

    # assert [x for x in A.__extensions__.keys()] == ["func1", "func2"]
