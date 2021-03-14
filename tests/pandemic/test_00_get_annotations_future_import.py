from __future__ import annotations

from typing import Any, get_type_hints

import pytest
from pydantic import BaseModel

from framework import AnyAnalyzer

"""
前方参照を用いると型が文字列となる。
__annotations__の参照では前方参照を解決できていない。
get_type_hintsを用いるのがよい。
"""


def test_get_type_hints_obj():
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

    obj: Any = None

    if obj := C:
        assert obj.__annotations__ == {"name": "str"}
        assert get_type_hints(obj) == {"name": str, "age": int}
        assert AnyAnalyzer.get_type_hints_from_current_frame(obj) == {
            "name": str,
            "age": int,
        }

    if obj := F:
        assert obj.__annotations__ == {"sex": "float"}
        assert get_type_hints(obj) == {"name": str, "age": int, "sex": float}
        assert AnyAnalyzer.get_type_hints_from_current_frame(obj) == {
            "name": str,
            "age": int,
            "sex": float,
        }

    if obj := func:
        assert obj.__annotations__ == {"name": "str"}
        assert get_type_hints(obj) == {"name": str}
        assert AnyAnalyzer.get_type_hints_from_current_frame(obj) == {"name": str}


def test_get_type_hints_func():
    class A:
        pass

    def func(obj: A):
        pass

    with pytest.raises(NameError):
        get_type_hints(func) == {"obj": A}

    assert AnyAnalyzer.get_type_hints_from_current_frame(func) == {"obj": A}
    assert AnyAnalyzer.get_signature(func).parameters["obj"].annotation == A

    def nest_analyzer():
        class B:
            pass

        def func(obj: B):
            pass

        with pytest.raises(NameError):
            get_type_hints(func) == {"obj": B}

        assert AnyAnalyzer.get_type_hints_from_current_frame(func) == {"obj": B}
        assert AnyAnalyzer.get_signature(func).parameters["obj"].annotation == B

    nest_analyzer()
