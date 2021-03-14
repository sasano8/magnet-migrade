from typing import List, Literal, Union
from uuid import UUID

from pydantic import Field

from framework import DateTimeAware

from ..commons import BaseModel


class Order(BaseModel):
    order_date: DateTimeAware = None
    result_info: dict = None
    bid_or_ask: Literal["ask", "bid"]
    order_type: Literal["market", "limit"] = "market"
    time_in_force: Literal["GTC", "IOC", "FOK"] = "GTC"
    currency_pair: str
    price: float = None
    amount: float = 0
    limit: float = None
    loss: float = None
    comment: str = None
    reason: str = ""
    sys_comment: str = "テスト中"


class Position(BaseModel):
    schema_version: int = Field(0, const=True)
    last_order_date: DateTimeAware = DateTimeAware(1950, 1, 1)
    entry_order: Union[Order, None] = None
    settle_order: Union[Order, None] = None


class BrokerABC:
    pass


class Broker:
    def __init__(self) -> None:
        self.orders: List[Order] = []  # 発注予定もしくは発注中
        self.positions: List[Position] = []  # 確定済みの注文はポジションとなる。

    def load_data(self):
        """データベースから注文とオーダー情報を取得する"""
        self.orders = []
        self.positions = []

    async def observe(self, state):
        while True:
            if state.is_cancelled:
                break

            # 買い　売りがある
            # 予約　発注済み　確定済みがある

            for order in self.orders:
                pass

            for order in self.positions:
                pass
