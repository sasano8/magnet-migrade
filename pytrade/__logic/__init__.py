from decimal import ROUND_DOWN, ROUND_HALF_UP, ROUND_UP, Decimal

from pydantic import BaseModel, Field, validate_arguments

__all__ = ["calc_unit_amount"]
# calculator　に移植


@validate_arguments
def calc_amount(
    budget: Decimal = Field(..., ge=0),
    real_price: Decimal = Field(..., gt=0),
    min_unit: Decimal = Field(default_factory=lambda: Decimal("0.01"), gt=0),
):
    """取引価格に対して、予算内で発注可能な数量を返す

    Args:
        budget (Decimal, optional): [description]. Defaults to Field(..., ge=0).
        real_price (Decimal, optional): [description]. Defaults to Field(..., gt=0).
        min_unit (Decimal, optional): [description]. Defaults to Field(default_factory=lambda: Decimal("0.01"), gt=0).

    Returns:
        [type]: [description]
    """
    amount = budget / real_price
    return amount.quantize(min_unit, rounding=ROUND_DOWN)


@validate_arguments
def calc_unit_amount(
    budget: Decimal = Field(..., ge=0),
    real_price: Decimal = Field(..., gt=0),
    min_unit: Decimal = Field(0, gt=0),
) -> Decimal:
    """最低取引単位に対して発注可能な数量を返す。

    Args:
        budget (Decimal, optional): [description]. Defaults to Field(..., ge=0).
        current_value (Decimal, optional): [description]. Defaults to Field(..., ge=0).
        min_unit (Decimal, optional): [description]. Defaults to Field("0.01", gt=0).

    Returns:
        Decimal: return ammount
    """
    if real_price <= 0:
        return Decimal("0")

    amount = budget / (real_price * min_unit)
    amount = amount.quantize(Decimal("0"), rounding=ROUND_DOWN)
    return amount


def infer_min_unit(price: Decimal):
    n = price.quantize(Decimal("0"), rounding=ROUND_DOWN)
    length = int(len(str(n)) / 2)
    return Decimal("0.1") ** length
