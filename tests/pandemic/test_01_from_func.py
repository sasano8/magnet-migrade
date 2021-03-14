# type: ignore
import inspect
from inspect import _ParameterKind as pkind
from typing import Any, Callable, Dict, Iterable

import pytest
from fastapi.params import Body, Depends, Param, Security
from pydantic import BaseModel, BaseSettings, Field

from framework.analyzers import FuncAnalyzer
from pandemic import SignatureBuilder
from pandemic.field import ModelFieldEx


class Person(BaseModel):
    name: str = "test"


def get_db():
    pass


def func(
    self,
    name,
    data: BaseModel,
    db=Depends(get_db),
    current_user=Security(),
    person=Person(),
    person2: Person = Person(),
    *args: Person,
    **kwargs: Person,
) -> int:
    pass


def func_kind_1(self, name, /, age, sex, *args, country, city, **kwargs):
    pass


def func_empty():
    pass


def test_signature_spec():
    """型注釈がない場合と、デフォルト値がない場合は、それぞれinspect._emptyを返すことを確認する。"""
    parameter = inspect.signature(func).parameters["self"]
    assert parameter.kind is pkind.POSITIONAL_OR_KEYWORD
    assert parameter.default is inspect._empty
    assert parameter.annotation is inspect._empty


def test_from_parameter_field_must_be():
    def must_be(param: inspect.Parameter, field: ModelFieldEx):
        assert param.name == field.name

        if param.annotation is inspect._empty:
            assert field.type_ is Any
        else:
            assert field.type_ is param.annotation

        if param.default is inspect._empty:
            assert field.required == True
            assert field.default is inspect._empty
        else:
            assert field.required == False
            assert param.default == field.default

        assert param.kind == field.kind

    sig = inspect.signature(func)
    from_parameter = SignatureBuilder.__normalizer__.from_parameter

    if name := "self":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "name":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "data":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "db":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "current_user":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "person":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "person2":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "args":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    if name := "kwargs":
        param = sig.parameters[name]
        field = from_parameter(param)
        must_be(param, field)

    sb = SignatureBuilder.from_func(func, normalizer=from_parameter)
    fields = {x.name: x for x in sb.get_fields()}

    assert sb.return_annotation == sig.return_annotation
    assert [x for x in fields.keys()] == [
        "self",
        "name",
        "data",
        "db",
        "current_user",
        "person",
        "person2",
        "args",
        "kwargs",
    ]
