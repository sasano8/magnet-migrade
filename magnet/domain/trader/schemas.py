import decimal
import logging
from typing import Literal, Optional

from pydantic import Field, validator

from framework import DateTimeAware

from ...commons import BaseModel
from .core import interfaces

logger = logging.getLogger(__name__)


class TradeDetector(BaseModel):
    id: int = None
    is_system: bool = False
    name: str
    description: str = ""
    code: str
    invert_ask_or_bid: bool = False

    @validator("code")
    def valid_code(cls, v, values, **kwargs):
        from . import algorithms

        name = values["name"]
        code = v
        invert_ask_or_bid = values.get("invert_ask_or_bid", False)
        func = algorithms.build_script(name, code, invert_ask_or_bid)

    @property
    def func(self):
        from . import algorithms

        func = algorithms.build_script(self.name, self.code)

        if not self.invert_ask_or_bid:
            return func

        def invert_func(topic):
            result = func(topic)
            if result == "ask":
                return "bid"
            elif result == "bid":
                return "ask"
            else:
                return result

        return invert_func


class OrderLogic(BaseModel):
    description: str = ""
    # order_type: Literal["market", "limit"] = "market"  # 指値・成り行き
    wallet: str = Field(None, description="どの財布を利用するか指定する")
    allocation_rate: decimal.Decimal = Field(
        0.7, gt=0, lt=1, description="財布から何％を割り当てるか指定する"
    )
    min_unit: decimal.Decimal = Field(0.01, gt=0, description="最低取引単位　ビットコインは0.01")
    ask_limit_rate: decimal.Decimal = Field(
        None, gt=1, description="ask時に何％の損益で利確するか指定する"
    )
    ask_loss_rate: decimal.Decimal = Field(
        None, lt=1, description="ask時に何％の減益でロスカットするか指定する"
    )
    bid_limit_rate: decimal.Decimal = Field(
        None, gt=1, description="bid時に何％の損益で利確するか指定する"
    )
    bid_loss_rate: decimal.Decimal = Field(
        None, lt=1, description="bid時に何％の減益でロスカットするか指定する"
    )

    def __init__(self, **kwargs):
        kwargs.pop("name", None)
        kwargs.pop("amount", None)
        kwargs.pop("algorithm", None)
        kwargs.pop("args", None)
        kwargs.pop("time_in_force", None)
        kwargs.pop("order_type", None)
        kwargs.pop("limit_rate", None)
        kwargs.pop("loss_rate", None)
        super().__init__(**kwargs)


class TradeProfile(BaseModel):
    class Config:
        orm_mode = True

    id: int
    version: int = 0
    name: str
    description: str = ""
    provider: str
    market: str
    product: str
    periods: int
    cron: str = ""
    broker: str
    # trade_rule: RuleTrade
    job_type: Literal["production", "virtual", "backtest", "test"] = "backtest"
    bet_strategy: Literal[
        "flat", "martingale", "grand_martingale", "parley", "dalambert", "pyramid"
    ] = None
    trade_type: str = "stop_and_reverse"
    monitor_topic: str = "yesterday_ticker"
    detector_name: str = "detect_t_cross"  # 最終的にはDSLでスクリプト化したい
    order_logic: OrderLogic

    def __init__(self, **kwargs):
        kwargs.pop("trade_rule", None)
        super().__init__(**kwargs)

    def calc_amount(self, price):
        if not price:
            return 0
        wallet = decimal.Decimal("30000")
        max_price = wallet * self.order_logic.allocation_rate
        amount = max_price / decimal.Decimal(str(price))
        amount = amount.quantize(
            self.order_logic.min_unit, rounding=decimal.ROUND_FLOOR
        )
        if self.order_logic.min_unit > amount:
            print("最低取引単位の数量に達していません。おそらく注文は無視されます。")
            return 0
        return amount

    def calc_limit(self, ask_or_bid, price):
        if not isinstance(price, decimal.Decimal):
            # TODO: priceをdecimal型にしておく
            logger.info("calc_limit: decimal型にしておけよ")
            price = decimal.Decimal(str(price))
        if self.order_logic.ask_limit_rate is not None and ask_or_bid == "ask":
            return price * self.order_logic.ask_limit_rate
        elif self.order_logic.bid_limit_rate is not None and ask_or_bid == "bid":
            return 2 * price - (price * self.order_logic.bid_limit_rate)
        else:
            return None

    def calc_loss(self, ask_or_bid, price):
        if not isinstance(price, decimal.Decimal):
            # TODO: priceをdecimal型にしておく
            logger.info("calc_limit: decimal型にしておけよ")
            price = decimal.Decimal(str(price))
        if self.order_logic.ask_loss_rate is not None and ask_or_bid == "ask":
            return price * self.order_logic.ask_loss_rate
        elif self.order_logic.bid_loss_rate is not None and ask_or_bid == "bid":
            return 2 * price - (price * self.order_logic.bid_loss_rate)
        else:
            return None

    def detect_limit_loss(self, price):
        if self.order_status is None:
            return None

        if self.order_status.entry_order is None:
            return None

        entry = self.order_status.entry_order
        if entry.bid_or_ask == "ask":
            if entry.limit and entry.limit < price:
                return "limit"
            elif entry.loss and entry.loss > price:
                return "loss"
        elif entry.bid_or_ask == "bid":
            if entry.limit and entry.limit > price:
                return "limit"
            elif entry.loss and entry.loss < price:
                return "loss"
        else:
            return None


TradeProfileCreate = TradeProfile.prefab("Create", exclude=["id"])
TradeProfilePatch = TradeProfile.prefab("Patch", optionals=...)


class TradeJob(TradeProfile):
    last_check_date: DateTimeAware = None
    order_status: interfaces.OrderStatus = None
    # is_backtest: bool = False
    # trade_type: str = "stop_and_reverse"
    # monitor_topic: str = "yesterday_ticker"
    # detector_name: str = "detect_t_cross"  # 最終的にはDSLでスクリプトをコンパイルするようにする

    @property
    def detector(self):
        return self.get_detector_by_name(self.detector_name)

    def get_detector_by_name(self, detector_name):
        if detector_name == "detect_t_cross":
            return self.detect_t_cross
        else:
            raise Exception()

    @property
    def topic(self):
        return None

    def get_topic_by_name(self, topic_name):
        if topic_name == "yesterday_ticker":
            return None
        else:
            raise Exception()


class TradeResult(BaseModel):
    job_id: int
    order_id: int = None
    msg: str
