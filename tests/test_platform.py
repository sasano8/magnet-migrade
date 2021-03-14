import pytest


def test_create_dic():
    dic1 = {"name": "bob", "age": 20}
    dic2 = {"name": "mary"}

    dic = {**dic1, **dic2}
    assert dic["name"] == "mary"
    assert dic["age"] == 20

    with pytest.raises(
        TypeError, match="got multiple values for keyword argument 'name'"
    ):
        dict(**dic1, **dic2)
