import asyncio
from dataclasses import dataclass
from typing import List, Literal, Protocol

from pydantic import BaseModel

from framework import DateTimeAware

# from ..domain.datastore.crud import CryptoOhlcDaily2
from ..domain.trader.crud import TradeResult
from ..domain.trader.schemas import TradeJob


class Job(Protocol):
    ...


class Broker(Protocol):
    ...


class Order(BaseModel):
    pass


class OrderDiactive(Order):
    """発注予定オーダー"""
    state: Literal["diactive"]


class OrderActive(Order):
    """発注済みオーダー"""
    state: Literal["active"]



class OrderPosition(Order):
    """確定したオーダーかつポジションとして監視が必要なオーダー"""
    state: Literal["position"]



class OrderSettled(Order):
    """ポジション決済済みオーダー"""
    state: Literal["settled"]



@dataclass
class Bot:
    job: Job
    broker: Broker
    schedule_interval: Literal["second", "daily", "monthly"]
    diactive_orders: List[Order]  # 発注予定の注文
    active_orders: List[Order]  # 発注済みかつ未確定の注文
    active_positions: List[Order]  # 決済するために監視する注文

    async def __call__(self):
        scheduler = [DateTimeAware(2020, 1, 1), DateTimeAware(2020, 1, 2)]
        for dt in scheduler:
            await self.stream(dt)

    def confirm_order(self, active_order: Order):
        self.active_orders.remove(active_order)
        self.active_positions.append(active_order)

    async def observe_orders(self):
        # 発注した注文が確定したか監視する
        for order in self.active_orders:
            # ブローカーから注文状況を取得する
            # 注文が確定していたら監視から外す？
            if orderded_id:
                self.confirm_order(active_order=order)
            else:
                pass

    async def stream(self, current_date: DateTimeAware):

        # 登場人物
        # 注文データ -> 注文毎にBotを作成するか？



        # 評価対象のデータを取得する（昨日分のデータ）
        # リミットロスを検知し、決済オーダーを出す
        # シグナルを検知して、新規オーダーを出す
