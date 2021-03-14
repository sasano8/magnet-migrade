# type: ignore
from enum import Enum
from typing import Literal

from framework.converters import Converter


def test_literal_to_enum():
    target = Literal["a", "b"]
    result = Converter.literal_to_enum(target)

    assert issubclass(result, Enum)
    assert isinstance(result.a, Enum)
    assert result.a.value == "a"
    assert result.b.value == "b"


def test_enum_to_dict_Enumのメンバが辞書にマップされること():
    class Target(Enum):
        a = "1"
        b = "2"

    result = Converter.enum_to_dict(Target)
    assert isinstance(result, dict)
    assert result == {"a": "1", "b": "2"}
