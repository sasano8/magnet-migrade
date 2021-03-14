import inspect

import pytest
from pydantic import BaseModel, ValidationError

from pandemic import SignatureBuilder, field
from pandemic.normalizers import Unpack


def test_cant_unpack_reason_conflict_name():
    def func(id: int):
        pass

    sb = SignatureBuilder.from_func(func)
    field = list(sb.get_fields())[0]
    fields = [field, field]

    SignatureBuilder.__unpacker__.assert_if_conflict_field_name(sb.get_fields())

    with pytest.raises(AssertionError, match="Conflict"):
        SignatureBuilder.__unpacker__.assert_if_conflict_field_name(fields)


def test_join_fields():
    def func1(name: str, unpack_as_age):
        pass

    def func2(age: int):
        pass

    sb1 = SignatureBuilder.from_func(func1)
    sb2 = SignatureBuilder.from_func(func2)

    fields = SignatureBuilder.join_fields(
        root_parameters={x.name: x for x in sb1.get_fields()},
        nest_parameters={"unpack_as_age": {x.name: x for x in sb2.get_fields()}},
    )

    assert len(fields) == 2
    assert fields["name"].type_ is str
    assert fields["age"].type_ is int


def test_join_fields_if_conflict_name():
    def func1(name: str, unpack_as_name):
        pass

    def func2(name: str):
        pass

    sb1 = SignatureBuilder.from_func(func1)
    sb2 = SignatureBuilder.from_func(func2)

    with pytest.raises(AssertionError, match="Conflict"):
        SignatureBuilder.join_fields(
            root_parameters={x.name: x for x in sb1.get_fields()},
            nest_parameters={"unpack_as_name": {x.name: x for x in sb2.get_fields()}},
        )

    with pytest.raises(AssertionError, match="Conflict"):
        SignatureBuilder.join_fields(
            root_parameters={x.name: x for x in sb1.get_fields()},
            nest_parameters={"unpack_as_name": {x.name: x for x in sb2.get_fields()}},
            conflict_validator=SignatureBuilder.__unpacker__.assert_if_conflict_field_name,
        )

    SignatureBuilder.join_fields(
        root_parameters={x.name: x for x in sb1.get_fields()},
        nest_parameters={"unpack_as_name": {x.name: x for x in sb2.get_fields()}},
        conflict_validator=lambda x: False,
    )


def test_unpack_forbidden_filter():
    """Can't unpack if kind is POSITIONAL_ONLY or VAR_POSITIONAL or VAR_KEYWORD."""

    def func(pos, /, pos_or_kw, *args, kw, **kwargs):
        pass

    filter_forbidden = SignatureBuilder.__unpacker__.filter_forbidden
    sb = SignatureBuilder.from_func(func)
    fields = {x.name: x for x in sb.get_fields()}

    if name := "pos":
        field = fields[name]
        assert field.kind == inspect._ParameterKind.POSITIONAL_ONLY
        assert filter_forbidden(field) == True

    if name := "pos_or_kw":
        field = fields[name]
        assert field.kind == inspect._ParameterKind.POSITIONAL_OR_KEYWORD
        assert filter_forbidden(field) == False

    if name := "args":
        field = fields[name]
        assert field.kind == inspect._ParameterKind.VAR_POSITIONAL
        assert filter_forbidden(field) == True

    if name := "kw":
        field = fields[name]
        assert field.kind == inspect._ParameterKind.KEYWORD_ONLY
        assert filter_forbidden(field) == False

    if name := "kwargs":
        field = fields[name]
        assert field.kind == inspect._ParameterKind.VAR_KEYWORD
        assert filter_forbidden(field) == True

    forbiddens = [x.name for x in fields.values() if filter_forbidden(x)]
    assert forbiddens == ["pos", "args", "kwargs"]

    msg = filter_forbidden.__doc__ + ".*pos.*args.*kwargs"
    assert msg.startswith(
        "Can't unpack for contains POSITIONAL_ONLY or VAR_POSITIONAL or VAR_KEYWORD."
    )

    with pytest.raises(AssertionError, match=msg):
        sb.raise_if_cant_unpack(forbidden=filter_forbidden)

    with pytest.raises(AssertionError, match=msg):
        sb.raise_if_cant_unpack()

    with pytest.raises(AssertionError, match=msg):
        sb.unpack(forbidden=filter_forbidden)

    with pytest.raises(AssertionError, match=msg):
        sb.unpack()

    sb.raise_if_cant_unpack(forbidden=lambda x: False)
    sb.unpack(forbidden=lambda x: False)


def test_unpackable_case_required():
    def func(name: str, model1: BaseModel, model2: Unpack):
        pass

    filter_unpackable = SignatureBuilder.__unpacker__.filter_default
    sb = SignatureBuilder.from_func(func)
    fields = {x.name: x for x in sb.get_fields()}

    if name := "name":
        field = fields[name]
        assert field.type_ is str
        assert not filter_unpackable(field)

    if name := "model1":
        field = fields[name]
        assert issubclass(field.type_, BaseModel)
        assert filter_unpackable(field)

    if name := "model2":
        field = fields[name]
        assert issubclass(field.type_, Unpack)
        assert not filter_unpackable(field)

    names = [x.name for x in sb.get_unpackable_fields(filter_unpackable)]
    assert names == ["model1"]
    assert names == [x.name for x in sb.get_unpackable_fields()]


def test_unpackable_case_optional():
    """デフォルト値が存在する引数はアンパック対象にならないこと"""

    def func(model1: BaseModel = BaseModel()):
        pass

    filter_unpackable = SignatureBuilder.__unpacker__.filter_default
    sb = SignatureBuilder.from_func(func)
    fields = {x.name: x for x in sb.get_unpackable_fields()}
    assert len(fields) == 0


def test_cant_unpack_reason_forbid_kind_arg():
    def func(pos, /, pos_or_kw, *args, kw, **kwargs):
        pass

    with pytest.raises(AssertionError, match="Can't unpack"):
        SignatureBuilder.from_func(func).unpack()


# TODO: SignatureBuilder.split_args
# TODO: SignatureBuilder.restore_args
# TODO: SignatureBuilder._generate_func


def test_unpack():
    class User(BaseModel):
        name: str
        age: int

    def func(id: int, data: User):
        pass

    sb = SignatureBuilder.from_func(func).unpack()
    fields = {x.name: x for x in sb.get_fields()}

    if field := fields["id"]:
        field.type_ is int

    if field := fields["name"]:
        field.type_ is str

    if field := fields["age"]:
        field.type_ is int

    assert len(fields) == 3


def test_unpack_order():
    """展開された引数はLast in されていくこと"""

    class User(BaseModel):
        name: str
        age: int

    def func1(id: int, data: User):
        pass

    def func2(data: User, id: int):
        pass

    sb1 = SignatureBuilder.from_func(func1).unpack()
    sb2 = SignatureBuilder.from_func(func2).unpack()

    expected = ["id", "name", "age"]
    assert ["name", "age", "id"] != expected
    assert [x.name for x in sb1.get_fields()] == expected
    assert [x.name for x in sb2.get_fields()] == expected


def test_get_func():
    """新たなシグネチャを持つ関数を実行し、期待する結果を得られること"""

    class User(BaseModel):
        name: str
        age: int

    def func(id: int, data: User):
        return {"id": id, "name": data.name, "age": data.age}

    new_func = SignatureBuilder.from_func(func).unpack().get_func()
    expected = {"id": 1, "name": "test", "age": 20}
    assert new_func(**expected) == expected

    with pytest.raises(ValidationError) as e:
        new_func(id=1, name="test")

    if info := e.value.errors()[0]:
        assert info["loc"] == ("age",)
        assert info["msg"] == "field required"
