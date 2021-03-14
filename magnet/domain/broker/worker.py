import asyncio
from abc import ABC, abstractclassmethod
from dataclasses import dataclass, field
from typing import Dict, List

from framework import Linq

from ...database import get_db
from .models import TradeOrder
from .schemas import TradeOrderCreate, TradeOrderCreated


def get_broker(provider: str, market: str, product: str):

    for db in get_db:
        # m = TradeOrderRepository.get_model()
        m = TradeOrder
        # TradeOrderRepository.all(db)
        query = TradeOrder.as_rep().query(db)

        inactive_orders = query.filter(
            m.market == market, m.product == product, m.provider == provider
        ).filter(m.order_at is None)


@dataclass
class Broker(ABC):
    provider: str = "cryptowatch"
    market: str = "bitflyer"
    product: str = "bitjpy"
    orders: Dict[int, TradeOrderCreate] = field(init=False)
    new_orders: List[TradeOrderCreate] = field(init=False)

    def __post_init__(self):
        self.orders = {}
        self.new_orders = []

    def fetch_from_db(self, provider: str, market: str, product: str):
        """データベースからオーダーを復元する"""
        for db in get_db():
            # m = TradeOrderRepository.get_model()
            m = TradeOrder
            # query = TradeOrderRepository.all(db)
            query = TradeOrder.as_rep().query(db)

            inactive_orders = query.filter(
                m.market == market, m.product == product, m.provider == provider
            ).filter(m.order_at == None)

            self.orders = {}
            for item in inactive_orders:
                self.orders[item.id] = TradeOrderCreated.from_orm(item)

    # @abstractclassmethod
    def fetch_from_api(self):
        """各種APIからデータを取得し、オーダー状況を最新化する。"""
        pass

    def push_to_db(self):
        """オーダー状況をデータベースに反映する"""
        pass

    async def refresh(self):
        partition = dict(
            provider=self.provider, market=self.market, product=self.product
        )

        self.fetch_from_db(**partition)
        # await self.fetch_from_api(**partition)
        self.push_to_db()

    def request_order(self, order: TradeOrderCreate):
        if not isinstance(order, TradeOrderCreate):
            raise TypeError()

        for db in get_db():
            result = TradeOrder.as_rep().create(db, **order.dict())
            obj = TradeOrderCreated.from_orm(result)
            self.orders[obj.id] = obj

    async def __call__(self):
        count = 0
        while True:
            # self.request_order(
            #     TradeOrderCreate(
            #         provider="cryptowatch",
            #         market="bitflyer",
            #         product="bitjpy",
            #         bid_or_ask="ask",
            #         order_type="market",
            #     )
            # )
            await self.refresh()
            print(self.orders)
            await asyncio.sleep(10)


class BitflyerBroker(Broker):
    pass
