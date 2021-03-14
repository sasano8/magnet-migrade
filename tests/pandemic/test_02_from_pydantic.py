# type: ignore
import inspect
from typing import Any

from pydantic import BaseModel
from pydantic.fields import Field, FieldInfo

from framework import AnyAnalyzer, analyzers
from pandemic import SignatureBuilder
from pandemic.normalizers import ModelFieldEx, Normalizers


def test_from_modelfield():
    class User(BaseModel):
        name: str = Field(...)
        age: int = Field(0, ge=0)
        dummy: list
        description: str = ""

        class Config:
            fields = {"dummy": "example"}

    annotations = AnyAnalyzer.get_type_hints(User)
    assert annotations["name"] is str
    assert annotations["age"] is int
    assert annotations["dummy"] is list
    assert annotations["description"] is str

    if modelfield := User.__fields__["name"]:
        assert modelfield.type_.__name__ == "str"
        field = Normalizers.from_modelfield(modelfield, 0, annotations=annotations)
        assert field.kind == inspect._ParameterKind.KEYWORD_ONLY
        assert field.type_ is str
        assert field.type_ is annotations[field.name]
        assert field.required
        assert field.get_default(None) is None
        assert field.get_mata(None) is None

    if modelfield := User.__fields__["age"]:
        assert modelfield.type_.__name__ == "ConstrainedIntValue"
        field = Normalizers.from_modelfield(modelfield, 0, annotations=annotations)
        assert field.kind == inspect._ParameterKind.KEYWORD_ONLY
        assert field.type_ is int
        assert field.type_ is annotations[field.name]
        assert not field.required
        assert field.get_default(None) == 0
        assert isinstance(field.get_mata(None), FieldInfo)

    if modelfield := User.__fields__["dummy"]:
        assert modelfield.type_.__name__ == "list"
        field = Normalizers.from_modelfield(modelfield, 0, annotations=annotations)
        assert field.kind == inspect._ParameterKind.KEYWORD_ONLY
        assert field.type_ is list
        assert field.type_ is annotations[field.name]
        assert field.required
        assert not field.get_default(None)
        assert isinstance(field.get_mata(None), FieldInfo)
        assert field.get_mata().alias == "example"

    if modelfield := User.__fields__["description"]:
        assert modelfield.type_.__name__ == "str"
        field = Normalizers.from_modelfield(modelfield, 0, annotations=annotations)
        assert field.kind == inspect._ParameterKind.KEYWORD_ONLY
        assert field.type_ is str
        assert field.type_ is annotations[field.name]
        assert not field.required
        assert field.get_default() == ""
        assert field.get_mata(None) is None
