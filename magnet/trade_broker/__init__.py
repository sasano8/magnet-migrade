import datetime
from decimal import Decimal
from typing import List, Literal, Union

from framework import DateTimeAware, Linq, MiniDB

from ..config import APICredentialBitflyer, APICredentialZaif
from ..trade_api import BitflyerAPI, CryptowatchAPI, ZaifAPI, enums, schemas
from .abc import BrokerBase, Order, OrderResult


class BrokerRepository(MiniDB[BrokerBase]):
    def instatiate(self, key: str) -> BrokerBase:
        cls = self.get(key)
        if cls:
            return cls()
        else:
            return None


brokers = BrokerRepository()


api_bitflyer = BitflyerAPI(
    api_key=APICredentialBitflyer().API_BITFLYER_API_KEY,
    api_secret=APICredentialBitflyer().API_BITFLYER_API_SECRET,
)
api_zaif = ZaifAPI(
    api_key=APICredentialZaif().API_ZAIF_API_KEY,
    api_secret=APICredentialZaif().API_ZAIF_API_SECRET,
)


# @brokers.add
class Zaif(BrokerBase):
    @staticmethod
    def valid_currency_pair(currency_pair: str) -> bool:
        currency_pairs: set = enums.zaif_currency_pair.__args__  # type: ignore
        if currency_pair in currency_pairs:
            return True
        else:
            return False

    @staticmethod
    def map_currency_pair(currency_pair: enums.cryptowatch_currency_pair) -> str:
        return enums.mapping_currency_pairs_cryptowatch_to_zaif[currency_pair]

    async def get_ticker(self, currency_pair: str):
        """指定した銘柄の最新の売買情報を取得する"""
        exchange_currency_pair = self.map_currency_pair(currency_pair)
        result = await api_zaif.get_ticker(currency_pair=exchange_currency_pair)
        now = DateTimeAware.utcnow()
        return schemas.TickerInfo(
            product_common=currency_pair,
            product=exchange_currency_pair,
            exchange="zaif",
            close_time=datetime.date(now.year, now.month, now.day + 1),
            current_time=now,
            last=result.last,
            high=result.high,
            low=result.low,
            volume=result.volume,
            quote_volume=None,
            vwap=result.vwap,
            # volume_by_product: float
            # bid=result.,
            # ask=result.high,
        )

    # currency_pair: str api_zaif.currency_pairs
    async def post_buy(self, order: Order):
        return await api_zaif.post_trade(
            currency_pair=currency_pair,
            action="bid",
            price=1,
            amount=1,
            limit=limit,
            comment=comment,
        )

    # currency_pair: str api_zaif.currency_pairs
    async def post_sell(self, order: Order):
        return await api_zaif.post_trade(
            currency_pair=currency_pair,
            action="ask",
            price=1,
            amount=1,
            limit=limit,
            comment=comment,
        )

    async def order(self, order: Order):
        raise NotImplementedError()

    async def check_duplicate(self):
        # 無限に発注されるとこまる
        # １つのアルゴリズムに対して１つポジションがあればよい
        # しかし、それはブローカーの責務ではないと思う
        raise NotImplementedError()

    async def observe(self):
        self.orders: List[Order] = []  # 発注予定もしくは発注中
        self.positions: List[Position] = []  # 確定済みの注文はポジションとなる。

        # 買い　売りがある
        # 予約　発注済み　確定済みがある

        for order in orders:
            pass

        for order in positions:
            pass
