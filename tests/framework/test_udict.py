from typing import Any

import hypothesis as hs
import hypothesis.strategies as st
import pytest

from framework import MappingDict, udict


def test_init():
    assert udict() == {}
    assert udict(k="v") == {"k": "v"}
    assert udict([("k", "v")]) == {"k": "v"}
    assert udict({"k": "v"}) == {"k": "v"}
    assert udict({"k": udict.undefined}) == {}


@hs.given(key=st.just("key"), val=st.from_type(type).flatmap(st.from_type))
def test_setitem(key: str, val: Any):
    dic = udict()
    dic[key] = val
    assert dic[key] is val


@hs.given(key=st.just("key"), val=st.just(udict.undefined))
def test_setitem_undefined(key: str, val: Any):
    dic = udict()
    dic[key] = val
    assert not key in dic


def test_fetch_attr():
    class A:
        def __init__(self, attr1, attr2) -> None:
            self.attr1 = attr1
            self.attr2 = attr2

    obj1 = A(attr1="val1", attr2=udict.undefined)

    dic = udict()
    dic.fetch_attr(obj1, "attr1")
    dic.fetch_attr(obj1, "attr2")
    dic.fetch_attr(obj1, "attr3")
    dic.fetch_attr(obj1, "attr4", None)
    dic.fetch_attr(obj1, "attr5", udict.undefined)

    assert dic == {
        "attr1": "val1",
        "attr4": None,
    }


def test_fetch_item():
    obj1 = {"key1": "val1", "key2": udict.undefined}

    dic = udict()
    dic.fetch_item(obj1, "key1")
    dic.fetch_item(obj1, "key2")
    dic.fetch_item(obj1, "key3")
    dic.fetch_item(obj1, "key4", None)
    dic.fetch_item(obj1, "key5", udict.undefined)

    assert dic == {
        "key1": "val1",
        "key4": None,
    }


def test_fetch_index():
    obj1 = ["val1", udict.undefined]

    dic = udict()
    dic.fetch_index(obj1, 0)
    dic.fetch_index(obj1, 1)
    dic.fetch_index(obj1, 2)
    dic.fetch_index(obj1, 3, None)
    dic.fetch_index(obj1, 4, udict.undefined)

    assert dic == {
        0: "val1",
        3: None,
    }


def test_override():
    dic = udict({"key": 0})
    dic["key"] = udict.undefined
    assert dic == {"key": 0}


def test_update():
    dic = udict()

    with pytest.raises(NotImplementedError):
        dic.update({"key": udict.undefined})


def test_setdefault():
    dic = udict()

    with pytest.raises(NotImplementedError):
        dic.setdefault("a", None)


def test_mappingdict_allow_extra_false():
    class Etl(MappingDict):
        allow_extra = False
        from_to = {"key1": "key2"}

    dic = Etl()
    dic["key1"] = 1
    assert len(dic) == 1
    assert dic["key2"] == 1

    dic = Etl({"key1": 1})
    assert len(dic) == 1
    assert dic["key2"] == 1

    with pytest.raises(KeyError, match="key2"):
        dic["key2"] = 2


def test_mappingdict_allow_extra_true():
    class Etl(MappingDict):
        allow_extra = True
        from_to = {"key1": "key2"}

    dic = Etl()
    dic["key1"] = 1
    assert len(dic) == 1
    assert dic["key2"] == 1

    dic = Etl({"key1": 1})
    assert len(dic) == 1
    assert dic["key2"] == 1

    dic["key2"] = 2
    assert dic["key2"] == 2
    dic["key3"] = 3
    assert dic["key3"] == 3
    assert len(dic) == 2


def test_mappingdict_undefined():
    class Etl1(MappingDict):
        allow_extra = True
        from_to = {"key1": "key2"}

    class Etl2(MappingDict):
        allow_extra = False
        from_to = {"key1": "key2"}

    d1 = Etl1()
    d1["key1"] = udict.undefined
    d1["key2"] = udict.undefined
    d1["key3"] = udict.undefined

    d2 = Etl2()
    d2["key1"] = udict.undefined
    d2["key2"] = udict.undefined
    d2["key3"] = udict.undefined

    assert len(d1) == 0
    assert len(d2) == 0
