# type: ignore
import pytest

from libs import decorators
from libs.decorators import Repoisotry, abstract


def test_new_init():
    class Dummy:
        def __new__(cls):
            self = super().__new__(cls)

            if hasattr(self, "name"):
                print("name: {}".format(self.name))
            else:
                print("no name")

            return self

        def __init__(self):
            self.name = "test1"

    obj = Dummy()
    assert obj.name == "test1"


def test_func_decorator_init():
    def return_value():
        return 1

    class Dummy(abstract.FuncDecorator):
        def wrapper(self, func, *args, **kwargs):
            return func(*args, **kwargs) + 10

    wrapper = Dummy()
    assert isinstance(wrapper, Dummy)
    wrapped = wrapper(return_value)
    assert wrapped() == 11

    @Dummy
    def return_value():
        return 2

    assert return_value() == 12

    @Dummy()
    def return_value():
        return 3

    assert return_value() == 13


def test_instantiate():
    @decorators.Instantiate
    class Dummy:
        def __init__(self):
            self.name = "test1"

    assert isinstance(Dummy, Dummy.__class__)
    assert Dummy.name == "test1"

    @decorators.Instantiate()
    class Dummy:
        def __init__(self):
            self.name = "test2"

    assert isinstance(Dummy, Dummy.__class__)
    assert Dummy.name == "test2"

    @decorators.Instantiate(name="test3")
    class Dummy:
        def __init__(self, name):
            self.name = name

    assert isinstance(Dummy, Dummy.__class__)
    assert Dummy.name == "test3"


def test_hook():
    hook_id = None

    def set_value(target):
        nonlocal hook_id
        hook_id = id(target)

    @decorators.Hook(func=set_value)
    def dummy():
        pass

    target_id = id(dummy)

    assert hook_id == target_id

    msg = "__init__() missing 1 required keyword-only argument: 'func'"
    # msg = "'Hook' object has no attribute 'hook_func'"
    with pytest.raises(TypeError) as e:

        @decorators.Hook
        def dummy():
            pass

    assert str(e.value) == msg


def test_repository_pydantic_bug():
    """
    https://github.com/samuelcolvin/pydantic/issues/1596
    pydanticのバグにより、Callableなメンバのデフォルト値の有無によって、メソッドとなるかファンクションになるかバインド方式が異なる。
    全てファンクションとして実行されることを確認する。
    """

    class Dummy:
        def __init__(self):
            pass

    cls = Repoisotry
    obj = Dummy()
    obj.key = "test"

    # デフォルト値で実行
    # selector = lambda obj: obj.key
    rep = cls()
    key = rep.key_selector("test")
    assert key == "test"

    # ファンクションであることを想定した実行
    selector = lambda obj: obj.key
    rep = cls(key_selector=selector)
    key = rep.key_selector(obj)
    assert key == "test"

    # メソッドであることを想定した実行
    msg = "<lambda>() missing 1 required positional argument: 'obj'"

    with pytest.raises(TypeError) as e:
        selector = lambda self, obj: obj.key
        rep = cls(key_selector=selector)
        key = rep.key_selector(obj)

    assert str(e.value) == msg


def test_repoistory():
    functions = decorators.Tag(key_selector=lambda func: func.__name__)

    @functions
    def return_value():
        return 1

    func = functions.get("return_value")

    assert return_value.__name__ == "return_value"
    assert func.__name__ == "return_value"
    assert return_value is func
    assert func() == 1

    msg = "duplicate key: return_value"
    with pytest.raises(ValueError) as e:

        @functions
        def return_value():
            return 1

    assert str(e.value) == msg


def test_map():
    from pydantic import BaseModel

    class Person(BaseModel):
        name: str
        age: int

    @decorators.MapDict
    def return_value() -> Person:
        return dict(name="test", age=20)

    obj = return_value()

    assert obj.name == "test"
    assert obj.age == 20

    class PersonRepository:
        @decorators.MapDict
        def return_value(self) -> Person:
            return dict(name="test2", age=100)

    rep = PersonRepository()
    obj = rep.return_value()

    assert obj.name == "test2"
    assert obj.age == 100
