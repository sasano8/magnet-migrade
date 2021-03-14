from decimal import ROUND_CEILING, ROUND_DOWN, ROUND_HALF_UP, ROUND_UP
from decimal import Decimal
from decimal import Decimal as D
from decimal import InvalidOperation, getcontext

import hypothesis as hs
import hypothesis.strategies as st
import pytest
from pydantic import ValidationError

from pytrade import logic


def test_calc_amount():
    unit = Decimal("0.1")
    assert logic.calc_amount(10000, 5000000.25, unit ** 10) == Decimal("0.0019999999")
    assert logic.calc_amount(10000, 5000000.25, unit ** 3) == Decimal("0.001")
    assert logic.calc_amount(10000, 5000000.25, unit ** 2) == Decimal("0")

    assert logic.calc_amount(10001, 5000000.25, unit ** 10) == Decimal("0.0020001998")
    assert logic.calc_amount(10001, 5000000.25, unit ** 3) == Decimal("0.002")
    assert logic.calc_amount(10001, 5000000.25, unit ** 2) == Decimal("0")


def test_calc_amount_exception():
    logic.calc_amount(budget=0, real_price=0.01)
    with pytest.raises(ValidationError) as e:
        logic.calc_amount(budget=-1, real_price=0.01)

    with pytest.raises(ValidationError) as e:
        logic.calc_amount(budget=0, real_price=0)

    with pytest.raises(ValidationError) as e:
        logic.calc_amount(budget=0, real_price=0.01, min_unit=0)


def test_calc_unit_amount_exceptions():
    logic.calc_unit_amount(budget=0, real_price=0.00001, min_unit=0.00001)

    with pytest.raises(ValidationError) as e:
        logic.calc_unit_amount(budget=-0, real_price=0.00001, min_unit=0)

    assert e.value.errors() == [
        {
            "ctx": {"limit_value": 0},
            "loc": ("min_unit",),
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt",
        }
    ]

    with pytest.raises(ValidationError) as e:
        logic.calc_unit_amount(budget=0, real_price=0, min_unit=0.00001)

    assert e.value.errors() == [
        {
            "ctx": {"limit_value": 0},
            "loc": ("real_price",),
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt",
        }
    ]
    with pytest.raises(ValidationError) as e:
        logic.calc_unit_amount(budget=-0.00001, real_price=0.00001, min_unit=0.00001)

    assert e.value.errors() == [
        {
            "ctx": {"limit_value": 0},
            "loc": ("budget",),
            "msg": "ensure this value is greater than or equal to 0",
            "type": "value_error.number.not_ge",
        }
    ]

    with pytest.raises(InvalidOperation):
        logic.calc_unit_amount(budget=Decimal("NaN"), real_price=0, min_unit=0)

    with pytest.raises(InvalidOperation):
        logic.calc_unit_amount(budget=0, real_price=Decimal("NaN"), min_unit=0)

    with pytest.raises(InvalidOperation):
        logic.calc_unit_amount(budget=0, real_price=0, min_unit=Decimal("NaN"))


def test_calc_unit_amount_must_be():

    assert (
        logic.calc_unit_amount(budget=D("10"), real_price=D("10"), min_unit=D("1")) == 1
    )
    assert (
        logic.calc_unit_amount(
            budget=D("9.999999"), real_price=D("10"), min_unit=D("1")
        )
        == 0
    )

    assert (
        logic.calc_unit_amount(
            budget=D("10"), real_price=D("10"), min_unit=D("1.000001")
        )
        == 0
    )
    assert (
        logic.calc_unit_amount(budget=D("10"), real_price=D("10"), min_unit=D("0.1"))
        == 10
    )
    assert (
        logic.calc_unit_amount(budget=D("10"), real_price=D("10.1"), min_unit=D("0.1"))
        == 9
    )
    assert (
        logic.calc_unit_amount(
            budget=D("10.1"), real_price=D("10.1"), min_unit=D("0.1")
        )
        == 10
    )
    assert (
        logic.calc_unit_amount(
            budget=D("10.000009"), real_price=D("10.1"), min_unit=D("0.1")
        )
        == 9
    )
    assert (
        logic.calc_unit_amount(budget=D("10"), real_price=D("1"), min_unit=D("10")) == 1
    )
    assert (
        logic.calc_unit_amount(
            budget=D("10.9999999999"), real_price=D("1.1"), min_unit=D("10")
        )
        == 0
    )
    assert (
        logic.calc_unit_amount(budget=D("11"), real_price=D("1.1"), min_unit=D("10"))
        == 1
    )


def test_calc_unit_amount_float():
    assert logic.calc_unit_amount(budget=10, real_price=10, min_unit=1) == 1
    assert logic.calc_unit_amount(budget=10, real_price=10, min_unit=1.000001) == 0
    assert logic.calc_unit_amount(budget=10.000009, real_price=10.1, min_unit=0.1) == 9
    assert (
        logic.calc_unit_amount(budget=10.9999999999, real_price=1.1, min_unit=10) == 0
    )
    assert logic.calc_unit_amount(budget=11, real_price=1.1, min_unit=10) == 1


@hs.given(
    budget=st.decimals(
        min_value=0,
        max_value=10000000000,
        allow_nan=False,
        allow_infinity=False,
        places=10,
    ),
    real_price=st.decimals(
        min_value=0.000000001,
        max_value=10000000000,
        allow_nan=False,
        allow_infinity=False,
        places=10,
    ),
    min_unit=st.decimals(
        min_value=0.000000001,
        max_value=10000000000,
        allow_nan=False,
        allow_infinity=False,
        places=10,
    ),
)
def test_calc_unit_amount_monkey(budget, real_price, min_unit):
    result = logic.calc_unit_amount(
        budget=budget, real_price=real_price, min_unit=min_unit
    )
    assert isinstance(result, Decimal)
    assert result >= 0


def test_infer_min_unit():
    assert logic.infer_min_unit(Decimal("0.1")) == Decimal("1")
    assert logic.infer_min_unit(Decimal("0")) == Decimal("1")
    assert logic.infer_min_unit(Decimal("5")) == Decimal("1")
    assert logic.infer_min_unit(Decimal("50")) == Decimal("0.1")
    assert logic.infer_min_unit(Decimal("500")) == Decimal("0.1")
    assert logic.infer_min_unit(Decimal("5000")) == Decimal("0.01")
    assert logic.infer_min_unit(Decimal("50000")) == Decimal("0.01")
    assert logic.infer_min_unit(Decimal("500000")) == Decimal("0.001")
    assert logic.infer_min_unit(Decimal("5000000")) == Decimal("0.001")
