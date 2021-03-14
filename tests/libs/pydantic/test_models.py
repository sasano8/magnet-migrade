# type: ignore
import pytest
from pydantic.error_wrappers import ValidationError

from libs.pydantic import BaseModel


def test_new_type():
    class Dummy(BaseModel):
        name: str = "test"
        age: int = 20

    assert "Dummy" == Dummy.__name__

    new_type = Dummy.new_type(prefix="New", suffix="Create")
    obj = new_type()
    assert "NewDummyCreate" == new_type.__name__
    assert hasattr(obj, "name")
    assert hasattr(obj, "age")

    dic = obj.dict()
    assert dic == {"name": "test", "age": 20}


def test_prefab_exclude():
    class Dummy(BaseModel):
        name: str = "test"
        age: int = 20

        class Config:
            extra = "forbid"

    # プレーンなBaseModelの挙動を確認
    assert Dummy().dict() == {"name": "test", "age": 20}

    # 指定したフィールドが除外されること
    new_type = Dummy.prefab(prefix="New", suffix="Create", exclude=("name",))
    obj = new_type()
    assert obj.dict() == {"age": 20}

    # 指定したフィールドが除外されること
    new_type = Dummy.prefab(prefix="New", suffix="Create", exclude=("name", "age"))
    obj = new_type()
    assert obj.dict() == {}

    # 全てのフィールドが除外されること
    new_type = Dummy.prefab(prefix="New", suffix="Create", exclude=...)
    obj = new_type()
    assert obj.dict() == {}

    # extra="forbid"の場合、除外したフィールドを初期化した場合はエラーが発生（デフォルトは、extra="ignore"）
    with pytest.raises(ValidationError, match="1 validation error") as e:
        assert new_type.Config.extra == "forbid"
        obj = new_type(name="test")


def test_prefab_optionals():
    class Dummy(BaseModel):
        name: str
        age: int

        class Config:
            extra = "forbid"

    # プレーンなBaseModelの挙動を確認（２個が必須フィールド）
    with pytest.raises(ValidationError, match="2 validation error") as e:
        obj = Dummy()

    # 指定したフィールドがオプションとなること（１個がオプションになる）
    new_type = Dummy.prefab(prefix="New", suffix="Create", optionals=("name",))
    with pytest.raises(ValidationError, match="1 validation error") as e:
        obj = new_type()

    # 指定したフィールドがオプションとなること（２個がオプションになる）
    new_type = Dummy.prefab(
        prefix="New",
        suffix="Create",
        optionals=(
            "name",
            "age",
        ),
    )
    obj = new_type()
    assert obj.dict() == {"name": None, "age": None}
    assert obj.dict(exclude_unset=True) == {}

    # ...を指定した場合、全てのフィールドがオプションとなること
    new_type = Dummy.prefab(prefix="New", suffix="Create", optionals=...)
    obj = new_type()
    assert obj.dict() == {"name": None, "age": None}
    dic = obj.dict(exclude_unset=True)
    assert dic == {}

    # 初期化確認
    obj = new_type(name="test", age=20)
    assert obj.dict() == {"name": "test", "age": 20}
    assert obj.dict(exclude_unset=True) == {"name": "test", "age": 20}


def test_prefab_requires():
    class Dummy(BaseModel):
        name: str = None
        age: int = None

    # 指定したフィールドが必須となること（１個のフィールドで検証）
    new_type = Dummy.prefab(prefix="New", suffix="Create", requires={"name"})
    with pytest.raises(ValidationError, match="1 validation error") as e:
        obj = new_type()

    # 指定したフィールドが必須となること（２個のフィールドで検証）
    new_type = Dummy.prefab(prefix="New", suffix="Create", requires={"name", "age"})
    with pytest.raises(ValidationError, match="2 validation error") as e:
        obj = new_type()

    # ...を指定した場合、全てのフィールドが必須となること
    new_type = Dummy.prefab(prefix="New", suffix="Create", requires=...)
    with pytest.raises(ValidationError, match="2 validation error") as e:
        obj = new_type()

    # 初期化確認
    obj = new_type(name="test", age=10)
    assert obj.dict() == {"name": "test", "age": 10}
    assert obj.dict(exclude_unset=True) == {"name": "test", "age": 10}


def test_prefab_complex_validation():
    """
    1. excludeに指定されたフィールドは初めに除外され、requires optionalsで指定することはできない
    2. requiresとoptionalsの優先順位は同等（同じフィールドを指定した場合エラーとなる）
    """

    class Dummy(BaseModel):
        name: str

    # excludeされたフィールドは、必須指定できないこと
    with pytest.raises(KeyError, match="name") as e:
        new_type = Dummy.prefab(
            prefix="New", suffix="Create", exclude=("name",), requires={"name"}
        )

    # excludeされたフィールドは、オプション指定できないこと
    with pytest.raises(KeyError, match="name") as e:
        new_type = Dummy.prefab(
            prefix="New", suffix="Create", exclude=("name",), optionals={"name"}
        )

    # requiresとoptionalsが衝突した場合エラーとなること
    with pytest.raises(KeyError, match="conflict required and optional field") as e:
        new_type = Dummy.prefab(
            prefix="New", suffix="Create", requires=("name",), optionals={"name"}
        )

    # requiresとoptionalsの両方に全てを指定することはできないこと
    with pytest.raises(
        KeyError, match="Only one of required and optionals can be specified as all"
    ) as e:
        new_type = Dummy.prefab(
            prefix="New", suffix="Create", requires=..., optionals=...
        )
