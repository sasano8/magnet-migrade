import asyncio
from decimal import Decimal
from typing import Any, Literal, Union

from pydantic import BaseModel, Field, root_validator

from framework import DateTimeAware

from ...commons import intellisense
from ...config import APICredentialBitflyer, APICredentialZaif
from ...trade_api import BitflyerAPI, ZaifAPI


@intellisense
class Order(BaseModel):
    currency_pair: str
    bid_or_ask: Literal["ask", "bid"]
    order_type: Literal["market", "limit"] = "market"
    time_in_force: Literal["GTC", "IOC", "FOK"] = Field("GTC", const=True)
    order_date: DateTimeAware = None
    result_info: dict = None
    price: float = None
    amount: float = 0
    limit: float = None
    loss: float = None
    comment: str = None
    reason: str = ""
    sys_comment: str = "テスト中"

    @property
    def is_done(self) -> bool:
        return self._is_done(self.order_date, self.result_info)

    @classmethod
    def _is_done(cls, order_date, result_info):
        if order_date is None and result_info is None:
            result = False
        elif order_date is not None and result_info is not None:
            result = True
        else:
            raise ValueError()
        return result

    @root_validator()
    def valid_status(cls, values):
        order_date = values.get("order_date", None)
        result_info = values.get("result_info", None)
        cls._is_done(order_date, result_info)
        return values

    def get_invert_bid_or_ask(self) -> str:
        if self.bid_or_ask == "ask":
            return "bid"
        elif self.bid_or_ask == "bid":
            return "ask"
        else:
            raise Exception()


from enum import Enum


class BuyAsk(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


# @dataclass
class BitflyerAPITest:
    client: BitflyerAPI

    def __init__(self) -> None:
        self.client = BitflyerAPI(
            api_key=APICredentialBitflyer().API_BITFLYER_API_KEY,
            api_secret=APICredentialBitflyer().API_BITFLYER_API_SECRET,
        )

    async def get_markets(self):
        """取り扱っている商品などを取得する。主にデバッグ用"""
        return await self.client.get_markets()

    def convert_to_order(self, order):
        return dict(
            product_code="FX_BTC_JPY",
            child_order_type="MARKET",
            side="BUY",
            size=0.01,
            minute_to_expire=60 * 60,
            time_in_force="GTC",
        )

    async def order(self, order):
        converted_order = self.convert_to_order(order)
        order_response = await self.client.post_sendchildorder(**converted_order)
        return converted_order, order_response

    async def get_order_data_if_completed(
        self, converted_order, order_response
    ) -> Union[Any, None]:
        """注文が全て約定していればデータを返す。そうでなければNone"""
        product_code = converted_order["product_code"]
        child_order_acceptance_id = order_response["child_order_acceptance_id"]
        status_data = await self.client.get_childorders(
            product_code=product_code,
            child_order_acceptance_id=child_order_acceptance_id,
        )
        return self.return_data(status_data)

    def return_data(self, status_data):
        # result = [{'id': 2453296368,
        # 'child_order_id': 'JFX20210315-162625-971434F',  # 注文の一部もしくは全部が約定した時に発行されるid
        # 'product_code': 'FX_BTC_JPY',
        # 'side': 'BUY',
        # 'child_order_type': 'MARKET',
        # 'price': 0.0,
        # 'average_price': 6489971.0,
        # 'size': 0.01,
        # 'child_order_state': 'COMPLETED',
        # 'expire_date': '2021-03-18T04:26:25',
        # 'child_order_date': '2021-03-15T16:26:25',
        # 'child_order_acceptance_id': 'JRF20210315-162625-040439',  #リクエストが受理された時に発行されるid
        # 'outstanding_size': 0.0,
        # 'cancel_size': 0.0,
        # 'executed_size': 0.01,
        # 'total_commission': 0.0}
        # ]
        all_completed = all(
            dic["child_order_state"] == "COMPLETED" for dic in status_data
        )
        if not all_completed:
            return None

        average_prices = []
        executed_sizes = []

        total_commission = Decimal("0")

        for x in status_data:
            total_commission += Decimal(str(x["total_commission"]))
            executed_sizes.append(Decimal(str(x["executed_size"])))
            average_prices.append(Decimal(str(x["average_price"])))

        average_price = sum(
            ave * siz for ave, siz in zip(average_prices, executed_sizes)
        )
        executed_size = sum(executed_sizes)
        return average_prices, executed_sizes, total_commission


class Broker:
    __clients__ = {"bitflyer": BitflyerAPITest()}
    __pairmap__ = {"zaif": {"btcjpy": "btc_jpy"}, "bitflyer": {"btcjpy": "FX_BTC_JPY"}}

    def __init__(self, client_name="bitflyer"):
        self.client = self.__clients__[client_name]

    async def __call__(self):
        dummy = {}
        try:
            converted_order, order_response = await self.client.order(dummy)
        except Exception as e:
            print(e)
            raise

        await asyncio.sleep(5)

        result = None
        try:
            result = await self.client.get_order_data_if_completed(
                converted_order, order_response
            )
        except Exception as e:
            print(e)
            raise

        if result:
            print(result)

    async def order(self, order):
        """発注する"""
        return await self.client.order(order)

    async def get_order_data_if_completed(self, converted_order, order_response):
        """apiから現在の注文情報を取得する"""
        return await self.client.get_order_data_if_completed(
            converted_order, order_response
        )
