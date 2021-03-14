from decimal import ROUND_FLOOR, Decimal

import hypothesis as hs
import pytest
from hypothesis import strategies as st
from pydantic import ValidationError

from pytrade.portfolio import Account, Portfolio, VirtualAccount


def test_validator():
    """基本的な入力可能範囲を検証する"""
    # floatは17桁を超えると丸めが発生します
    rounded = 1.0000000000000001
    significant_digits = 1.000000000000001
    assert rounded == 1
    assert significant_digits == 1.000000000000001

    VirtualAccount(name="va1", allocation_rate=rounded)

    VirtualAccount(name="va1", allocated_margin=0)
    with pytest.raises(ValidationError):
        VirtualAccount(name="va1", allocated_margin=-0.999999999999999)

    VirtualAccount(name="va1", allocation_rate=0)
    with pytest.raises(ValidationError):
        VirtualAccount(name="va1", allocation_rate=-0.999999999999999)

    with pytest.raises(ValidationError):
        VirtualAccount(name="va1", allocation_rate=1.000000000000001)

    with pytest.raises(ValidationError):
        Account(name="pa1", margin=-0.999999999999999)


def test_conflict_id():
    va1 = VirtualAccount(id=1)
    va2 = VirtualAccount(id=1)

    with pytest.raises(ValidationError) as e:
        Account(id=1, accounts=[va1, va2])

    assert e.value.errors() == [
        {
            "loc": ("accounts",),
            "msg": "1: conflict account id",
            "type": "value_error.conflictid",
        }
    ]

    pa1 = Account(id=1)
    pa2 = Account(id=1)

    with pytest.raises(ValidationError) as e:
        Portfolio(name="po1", accounts=[pa1, pa2])

    assert e.value.errors() == [
        {
            "loc": ("accounts",),
            "msg": "1: conflict account id",
            "type": "value_error.conflictid",
        }
    ]
    with pytest.raises(ValidationError) as e:
        Portfolio.parse_obj(
            {
                "name": "po1",
                "accounts": [
                    {"id": 1, "accounts": [{"id": 2}, {"id": 2}]},
                    {"id": 1, "accounts": [{"id": 2}, {"id": 2}]},
                ],
            }
        )

    assert e.value.errors() == [
        {
            "loc": ("accounts", 0, "accounts"),
            "msg": "2: conflict account id",
            "type": "value_error.conflictid",
        },
        {
            "loc": ("accounts", 1, "accounts"),
            "msg": "2: conflict account id",
            "type": "value_error.conflictid",
        },
    ]


def test_conflict_id_between_virtual_account():
    va1 = VirtualAccount(id=1)
    va2 = VirtualAccount(id=1)
    pa1 = Account(id=1, accounts=[va1])
    pa2 = Account(id=2, accounts=[va2])

    assert va1.id == va2.id
    assert pa1.id != pa2.id

    with pytest.raises(ValidationError) as e:
        Portfolio(name="po1", accounts=[pa1, pa2])

    assert e.value.errors() == [
        {
            "loc": ("accounts",),
            "msg": "2.1: conflict virtual account id",
            "type": "value_error.conflictid",
        }
    ]


def test_over_allocation():
    """物理アカウントの証拠金を超える仮想アカウントの証拠金割当計画は不可とする"""
    va1 = VirtualAccount(id=1, name="va1", allocation_rate=1)
    va2 = VirtualAccount(id=2, name="va2", allocation_rate=0.0001)

    with pytest.raises(ValidationError) as e:
        pa1 = Account(name="pa1", accounts=[va1, va2])

    assert e.value.errors() == [
        {
            "loc": ("accounts",),
            "msg": "Can't allocation `allocation rate` over 100% -> 1.0001",
            "type": "value_error.overallocated",
        }
    ]


def test_allocated_margin_empty():
    va = VirtualAccount(name="va1")
    pa = Account(name="pa")
    po = Portfolio(name="po")

    assert va.allocated_margin == 0
    assert pa.allocated_margin == 0
    assert po.allocated_margin == 0


def test_allocated_margin_and_free_margin():
    va1 = VirtualAccount(name="va1", allocation_rate=0)
    pa1 = Account(name="pa1", accounts=[va1], margin=100)

    assert pa1.margin == 100
    assert pa1.free_margin == 100
    assert pa1.allocated_margin == 0
    assert pa1.allocated_margin == pa1.margin * va1.allocation_rate


def test_allocated_margin_va_one():
    va1 = VirtualAccount(name="va1", allocated_margin=100)
    pa1 = Account(name="pa1", accounts=[va1])
    po = Portfolio(name="po", accounts=[pa1])

    assert va1.allocated_margin == 100
    assert pa1.allocated_margin == 100
    assert po.allocated_margin == 100


def test_allocated_margin_va_two():
    va1 = VirtualAccount(id=1, name="va1", allocated_margin=100)
    va2 = VirtualAccount(id=2, name="va2", allocated_margin=200)
    pa1 = Account(id=1, name="pa1", accounts=[va1, va2])
    po = Portfolio(name="po", accounts=[pa1])

    assert va1.allocated_margin == 100
    assert va2.allocated_margin == 200
    assert pa1.allocated_margin == 300
    assert po.allocated_margin == 300


def test_allocated_margin_va_two_pa_two():
    va1 = VirtualAccount(id=1, name="va1", allocated_margin=100)
    va2 = VirtualAccount(id=2, name="va2", allocated_margin=200)
    va3 = VirtualAccount(id=3, name="va3", allocated_margin=400)
    va4 = VirtualAccount(id=4, name="va4", allocated_margin=800)
    pa1 = Account(id=1, name="pa1", accounts=[va1, va2])
    pa2 = Account(id=2, name="pa2", accounts=[va3, va4])
    po = Portfolio(name="po", accounts=[pa1, pa2])

    assert va1.allocated_margin == 100
    assert va2.allocated_margin == 200
    assert va3.allocated_margin == 400
    assert va4.allocated_margin == 800
    assert pa1.allocated_margin == 300
    assert pa2.allocated_margin == 1200
    assert po.allocated_margin == 1500

    assert pa1.margin == 0
    assert pa2.margin == 0
    assert po.margin == 0


def test_margin_va_two_pa_two():
    va1 = VirtualAccount(id=1, name="va1", allocated_margin=100)
    va2 = VirtualAccount(id=2, name="va2", allocated_margin=200)
    va3 = VirtualAccount(id=3, name="va3", allocated_margin=400)
    va4 = VirtualAccount(id=4, name="va4", allocated_margin=800)
    pa1 = Account(id=1, name="pa1", accounts=[va1, va2], margin=1600)
    pa2 = Account(id=2, name="pa2", accounts=[va3, va4], margin=3200)
    po = Portfolio(name="po", accounts=[pa1, pa2])

    assert va1.allocated_margin == 100
    assert va2.allocated_margin == 200
    assert va3.allocated_margin == 400
    assert va4.allocated_margin == 800
    assert pa1.allocated_margin == 300
    assert pa2.allocated_margin == 1200
    assert po.allocated_margin == 1500

    assert pa1.margin == 1600
    assert pa2.margin == 3200
    assert po.margin == 4800


def test_reallocation_allocation_all_with_margin_0():
    va1 = VirtualAccount(name="va1", allocation_rate=1)
    pa1 = Account(name="pa1", accounts=[va1])
    po = Portfolio(name="po", accounts=[pa1])

    new_po = po.reallocation()

    assert new_po.accounts[0].accounts[0].allocated_margin == 0
    assert new_po.accounts[0].allocated_margin == 0
    assert new_po.accounts[0].margin == 0
    assert new_po.allocated_margin == 0
    assert new_po.margin == 0


def test_reallocation_va_one():
    va1 = VirtualAccount(name="va1", allocation_rate=1)
    pa1 = Account(name="pa1", accounts=[va1], margin=100)
    po = Portfolio(name="po", accounts=[pa1])

    new_po = po.reallocation()

    assert new_po.accounts[0].accounts[0].allocated_margin == 100
    assert new_po.accounts[0].allocated_margin == 100
    assert new_po.accounts[0].margin == 100
    assert new_po.allocated_margin == 100
    assert new_po.margin == 100


def test_reallocation_va_two():
    va1 = VirtualAccount(id=1, name="va1", allocation_rate=0.5)
    va2 = VirtualAccount(id=2, name="va2", allocation_rate=0.5)
    pa1 = Account(name="pa1", accounts=[va1, va2], margin=100)
    po = Portfolio(name="po", accounts=[pa1])

    new_po = po.reallocation()

    assert new_po.accounts[0].accounts[0].allocated_margin == 50
    assert new_po.accounts[0].accounts[1].allocated_margin == 50
    assert new_po.accounts[0].allocated_margin == 100
    assert new_po.accounts[0].margin == 100
    assert new_po.allocated_margin == 100
    assert new_po.margin == 100


def test_reallocation_va_two_pa_two():
    va1 = VirtualAccount(id=1, name="va1", allocation_rate=0)
    va2 = VirtualAccount(id=2, name="va2", allocation_rate=1)
    va3 = VirtualAccount(id=3, name="va3", allocation_rate=0.4)
    va4 = VirtualAccount(id=4, name="va4", allocation_rate=0.6)
    pa1 = Account(id=1, name="pa1", accounts=[va1, va2], margin=200)
    pa2 = Account(id=2, name="pa2", accounts=[va3, va4], margin=100)
    po = Portfolio(name="po", accounts=[pa1, pa2])

    new_po = po.reallocation()

    assert new_po.accounts[0].accounts[0].allocated_margin == 0
    assert new_po.accounts[0].accounts[1].allocated_margin == 200
    assert new_po.accounts[1].accounts[0].allocated_margin == 40
    assert new_po.accounts[1].accounts[1].allocated_margin == 60

    assert new_po.accounts[0].margin == 200
    assert new_po.accounts[0].allocated_margin == 200
    assert new_po.accounts[1].margin == 100
    assert new_po.accounts[1].allocated_margin == 100

    assert new_po.allocated_margin == 300
    assert new_po.margin == 300


def test_raise_if_allocated_over_margin():
    """仮想口座の証拠金合計が物理口座の証拠金合計を超えた時例外が発生する。
    ただし、仮想口座で利益が上がった時、仮想口座に計上することを考慮し、検証タイミングは任意とする。
    """
    va1 = VirtualAccount(name="va1", allocated_margin=1)
    pa1 = Account(name="pa1", accounts=[va1], margin=0)
    po = Portfolio(name="po", accounts=[pa1])
    with pytest.raises(ValidationError, match="value_error.overmargin"):
        po.raise_if_allocated_over_margin()


def test_raise_if_over_allocation_rate():
    """仮想口座に100%を超える証拠金割当率を設定することはできない"""
    va1 = VirtualAccount(id=1, name="va1", allocation_rate=0.5)
    va2 = VirtualAccount(id=2, name="va1", allocation_rate=0.51)
    with pytest.raises(ValidationError, match="value_error.overallocated"):
        pa1 = Account(name="pa1", accounts=[va1, va2], margin=100)


@hs.given(rate=st.floats(min_value=0, max_value=1))
def test_reallocation_must_be_not_raise_exception(rate):
    """証拠金割当率が100%に収まる時例外が発生することはない"""
    rate1 = 1 - rate
    rate2 = rate
    va1 = VirtualAccount(name="va1", allocation_rate=rate1)
    va1 = VirtualAccount(name="va1", allocation_rate=rate2)
    pa1 = Account(name="pa1", accounts=[va1], margin=100)
    po = Portfolio(name="po", accounts=[pa1])

    new_po = po.reallocation()


def test_reallocation_round():
    """証拠金割当時に端数は切り捨てられること"""
    va1 = VirtualAccount(name="va1", allocation_rate=0.15437)
    pa1 = Account(name="pa1", accounts=[va1], margin=123.053)
    po = Portfolio(name="po", accounts=[pa1])

    new_po = po.reallocation()
    assert new_po.accounts[0].accounts[0].allocated_margin == Decimal("18")

    # 根拠
    assert Decimal(str(123.053)) * Decimal(str(0.15437)) == Decimal("18.99569161")
    assert Decimal("18.99569161").quantize(
        Decimal("0"), rounding=ROUND_FLOOR
    ) == Decimal("18")
