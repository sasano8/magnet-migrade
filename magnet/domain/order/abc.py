import asyncio
import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Literal, Type

from .models import TradeProfile
from .schemas import BuyAndSellSignal, DealMessage, PreOrder, TradeResult

logger = logging.getLogger(__name__)


class HasName:
    @classmethod
    def get_name(cls):
        return cls._name


# class BrokerImpl(HasName):
#     # @classmethod
#     # def get_name(cls):
#     #     return cls.__name

#     def get_test_broker(self):
#         return TestBroker(self)


class BrokerImpl(HasName):
    def __init__(self, broker):
        self.client = broker

    def get_test_broker(self):
        return TestBroker(self)

    # def create_pre_order(
    #     self,
    #     budget: Decimal,
    #     product_code: str,
    #     side: Literal[1, -1],
    #     target_price: Decimal,
    #     limit_rate: Decimal = None,
    #     stop_rate: Decimal = None,
    # ):
    #     # product_code_localized = self.localize_product_code(product_code)
    #     size = PreOrder.calc_amount(
    #         budget=Decimal("100000"), price=target_price, min_unit=Decimal("0.01")
    #     )
    #     order = PreOrder(
    #         product_code=product_code,
    #         product_code_localized=product_code,
    #         side=side,
    #         target_price=target_price,
    #         size=size,
    #         limit_rate=limit_rate,
    #         stop_rate=stop_rate,
    #     )
    #     # order = self.on_create_order(order)
    #     return order

    def localize_order(self, order: PreOrder) -> PreOrder:
        """create_preorderの際に呼ばれるマーケット毎のローカライズ処理を実装する。主に、sideとproduct_codeをローカライズする。"""
        return order

    # def get_product_code_mapping(self) -> Dict[str, str]:
    #     return None

    # def localize_product_code(self, product_code: str) -> str:
    #     raise NotImplementedError()

    async def get_markets(self):
        raise NotImplementedError()

    async def get_ticker(self, product_code):
        raise NotImplementedError()

    async def order_test(self):
        raise NotImplementedError()

    def localize_product_code(self, product_code: str) -> str:
        return product_code

    async def order(self, order):
        """発注する"""
        raise NotImplementedError()

    async def cancel(self, status_data):
        """注文をキャンセルする。主に、リミットストップなどの付与注文をキャンセルするために使う。キャンセル済みの場合はNoneを返す。status_dataがNoneの時、Noneを返す。"""
        if status_data is None:
            return None
        return await self.order_cancel(status_data)

    async def order_cancel(self, status_data):
        """注文をキャンセルする。キャンセル済みの場合はNoneを返す。このメソッドはオーバーライド用のメソッドのため、クライアントとして利用する場合はcancelを利用してください。"""
        raise NotImplementedError()

    # async def close(self, finalized_data: TradeResult):
    #     """ブローカーにクローズ専用の処理は不要。単に注文を出せばよい"""
    #     raise NotImplementedError()

    # async def order_close(self, finalized_data):
    #     """エントリーに対する反対売買を行う。"""
    #     raise NotImplementedError()

    async def fetch_order_status(self, accepted_data):
        """apiから現在の注文情報を取得する"""
        raise NotImplementedError()

    async def fetch_order_status_until_complete(self, accepted_data):
        """注文が確定するまで待機する。注文のキャンセルなど、確定を想定できない状況で使用すると無限ループが生じる。"""
        if accepted_data is None:
            return

        while True:
            status_data = await self.fetch_order_status(accepted_data)
            if self.is_completed(status_data):
                return status_data
            await asyncio.sleep(10)

    def is_completed(self, status_data) -> bool:
        """全ての注文が約定・キャンセル・失効であることを確認する"""
        raise NotImplementedError()

    async def finalize(self, status_data) -> TradeResult:
        """is_completeな状態の時、全ての約定情報のサマリを返す"""
        raise NotImplementedError()


@dataclass
class TopicProvider(HasName):
    profile: TradeProfile
    broker: BrokerImpl

    def __post_init__(self):
        pass

    @classmethod
    def get_alias(cls) -> str:
        """辞書に格納するtopic_nameを指定する。test_current_tickerなど、current_tickerに擬態するような使い方をする"""
        return cls.get_name()

    async def get_topic(self, current_dt):
        raise NotImplementedError()


class Analyzer(HasName):
    __topics__: List[str] = []

    def __init__(self):
        self.__post_init__()

    def __post_init__(self):
        pass

    async def __call__(self, topic):
        pass


class TestBroker:
    def __init__(self, broker: BrokerImpl):
        self.client = broker

    async def run_test(self, timeout=100):
        accepted_data = await self.order_test()
        count = 0
        while count < timeout:
            await asyncio.sleep(1)

            status_data = await self.fetch_order_status(accepted_data)
            if not (is_completed := await self.is_completed(status_data)):
                count += 1

                accepted_cancel_order = await self.order_cancel(status_data)
                accepted_cancel_order = await self.order_cancel(status_data)
                continue

            result = await self.finalize(status_data)
            return result

        raise TimeoutError()

    def localize_product_code(self, product_code: str) -> str:
        return self.client.localize_product_code(product_code)

    async def get_markets(self):
        return await self.client.get_markets()

    async def get_ticker(self, product_code):
        return await self.client.get_ticker(product_code)

    async def order_test(self):
        return await self.client.order_test()

    async def order(self, order):
        """発注する"""
        logger.info(f"[ORDER]: {order}")
        accepted_data = await self.client.order(order)
        return accepted_data

    async def order_cancel(self, status_data):
        """注文をキャンセルする。キャンセル済みの場合はNoneを返す"""
        logger.info(f"[CANCEL]: {status_data}")
        accepted_cancel_data = await self.client.order_cancel(status_data)
        return accepted_cancel_data

    async def fetch_order_status(self, accepted_data):
        """apiから現在の注文情報を取得する"""
        status_data = await self.client.fetch_order_status(accepted_data)
        return status_data

    async def is_completed(self, status_data):
        """全ての注文が約定・キャンセル・失効であることを確認する"""
        return await self.client.is_completed(status_data)

    async def finalize(self, status_data):
        """is_completeな状態の時、全ての約定情報のサマリを返す"""
        return await self.client.finalize(status_data)
