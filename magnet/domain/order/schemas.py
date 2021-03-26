from decimal import Decimal
from typing import Any, DefaultDict, Literal, Optional, Tuple, Union

from pydantic import root_validator, validator

from pytrade import calculator
from pytrade.portfolio import AskBid, PositionStatus
from pytrade.stream import BuyAndSellSignal, DealMessage

from ...commons import BaseModel, intellisense


@intellisense
class PreOrder(BaseModel):
    product_code: str
    side: Literal[1, -1]
    target_price: Decimal
    size: Decimal
    limit_rate: Decimal = None
    stop_rate: Decimal = None

    @validator("limit_rate")
    def check_limit_range(cls, value, values):
        side = values.get("side")
        limit_rate = value

        if limit_rate is not None:
            if side == 1:
                if not limit_rate > 1:
                    raise ValueError(f"有効なリミット範囲ではありません。[{side}]: {limit_rate}")
            else:
                if not limit_rate < 1:
                    raise ValueError(f"有効なリミット範囲ではありません。[{side}]: {limit_rate}")

        return value

    @validator("stop_rate")
    def check_stop_range(cls, value, values):
        side = values.get("side")
        stop_rate = value

        if stop_rate is not None:
            if side == 1:
                if not stop_rate < 1:
                    raise ValueError(f"有効なストップ範囲ではありません。[{side}]: {stop_rate}")
            else:
                if not stop_rate > 1:
                    raise ValueError(f"有効なストップ範囲ではありません。[{side}]: {stop_rate}")

        return value

    @root_validator(skip_on_failure=True)  # limit_rate stop_rateの検証失敗時にはスキップする
    def check_limit(cls, values):
        limit_rate = values.get("limit_rate", None)
        stop_rate = values.get("stop_rate", None)

        # 注文処理が面倒なので、両方Noneかそうじゃないかだけ許容する
        if limit_rate is not None:
            if stop_rate is None:
                raise ValueError(f"limit_rateとstop_rateは互いに有効もしくは無効でなければいけません。")

        if limit_rate is None:
            if stop_rate is not None:
                raise ValueError(f"limit_rateとstop_rateは互いに有効もしくは無効でなければいけません。")

        return values

    @property
    def is_limit_stop(self):
        return self.limit_rate is not None and self.stop_rate is not None

    @property
    def limit_price(self):
        """エントリー方向の利確価格を返す"""
        if self.limit_rate is None:
            return None
        else:
            return self.target_price * self.limit_rate

    @property
    def stop_price(self):
        """エントリー方向と逆の損切価格を返す"""
        if self.stop_rate is None:
            return None
        else:
            return self.target_price * self.stop_rate

    @staticmethod
    def calc_amount(budget: Decimal, price: Decimal, min_unit: Decimal) -> Decimal:
        amount = calculator.calc_amount(
            budget=budget, real_price=price, min_unit=min_unit
        )
        return amount


@intellisense
class PreOrderLocalized(PreOrder):
    product_code_localized: str
    side_localized: Any


@intellisense
class OrderResult(BaseModel):
    average_price: Decimal
    executed_size: Decimal
    total_commission: Decimal
    other_commission: Decimal = Decimal("0")

    @classmethod
    def empty(cls):
        return cls(
            average_price=Decimal("0"),
            executed_size=Decimal("0"),
            total_commission=Decimal("0"),
            other_commission=Decimal("0"),
        )


@intellisense
class RemainOrder(BaseModel):
    side: int
    size: Decimal


@intellisense
class TradeResult(BaseModel):
    product_code_localized: str
    buy: Optional[OrderResult]
    sell: Optional[OrderResult]

    @property
    def size(self):
        assert self.buy.executed_size == self.sell.executed_size
        return self.buy.executed_size

    @classmethod
    def convert_to_empty_if_none(cls, value):
        if value is None:
            return OrderResult.empty()
        else:
            return value

    @validator("buy")
    def check_buy_is_none(cls, value):
        return cls.convert_to_empty_if_none(value)

    @validator("sell")
    def check_sell_is_none(cls, value):
        return cls.convert_to_empty_if_none(value)

    def get_remain(self) -> Union[RemainOrder, None]:
        """未決済のポジション（side, size）またはNoneを返す"""
        remain = self.buy.executed_size - self.sell.executed_size  # type: ignore

        if remain == 0:
            return None

        if remain > 0:
            side = 1
        else:
            side = -1

        return RemainOrder(side=side, size=abs(remain))

    @classmethod
    def merge_from_dict(cls, entry, counter):
        e = TradeResult.parse_obj(entry)
        c = TradeResult.parse_obj(counter)
        return cls.merge(e, c)

    @classmethod
    def merge(cls, entry: "TradeResult", counter: "TradeResult"):
        buy_total_commission = entry.buy.total_commission + counter.buy.total_commission
        buy_other_commission = entry.buy.other_commission + counter.buy.other_commission
        buy_executed_size = entry.buy.executed_size + counter.buy.executed_size
        buy_average_price = (
            (entry.buy.average_price * entry.buy.executed_size)
            + (counter.buy.average_price * counter.buy.executed_size)
        ) / buy_executed_size

        sell_total_commission = (
            entry.sell.total_commission + counter.sell.total_commission
        )
        sell_other_commission = (
            entry.sell.other_commission + counter.sell.other_commission
        )

        sell_executed_size = entry.sell.executed_size + counter.sell.executed_size
        sell_average_price = (
            (entry.sell.average_price * entry.sell.executed_size)
            + (counter.sell.average_price * counter.sell.executed_size)
        ) / sell_executed_size

        result = TradeResult(
            product_code_localized=entry.product_code_localized,
            buy=OrderResult(
                average_price=buy_average_price,
                executed_size=buy_executed_size,
                total_commission=buy_total_commission,
                other_commission=buy_other_commission,
            ),
            sell=OrderResult(
                average_price=sell_average_price,
                executed_size=sell_executed_size,
                total_commission=sell_total_commission,
                other_commission=sell_other_commission,
            ),
        )

        assert result.buy.executed_size == result.sell.executed_size  # type: ignore
        return result
