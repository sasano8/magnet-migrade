import datetime
from decimal import Decimal
from typing import Literal, Union

from framework import DateTimeAware, MiniDB

from ...config import APICredentialBitflyer, APICredentialZaif
from ...trade_api import BitflyerAPI, CryptowatchAPI, ZaifAPI, enums, schemas
from .core.interfaces import BrokerBase, Order, OrderResult


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


@brokers.add
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


@brokers.add
class Bitflyer(BrokerBase):
    @staticmethod
    def valid_currency_pair(currency_pair: str) -> bool:
        currency_pairs = enums.bitflyer_currency_pair.__args__
        if currency_pair in currency_pairs:
            return True
        else:
            return False

    @staticmethod
    def map_currency_pair(currency_pair: enums.cryptowatch_currency_pair) -> str:
        return enums.mapping_currency_pairs_cryptowatch_to_bitflyer[currency_pair]

    async def get_ticker(self, currency_pair: str):
        exchange_currency_pair = self.map_currency_pair(currency_pair)
        now = DateTimeAware.utcnow()

        b_result = await api_bitflyer.get_ticker(product_code=exchange_currency_pair)
        now = b_result.timestamp
        close_time = DateTimeAware(now.year, now.month, now.day + 1)

        # bitflyerは高値安値などをapiで取得できないため、cryptowatchで代替する
        # 集計中の本日の最新値を取得したい。close_time(現在日＋１)で本日更新中のレコードを取得できる。
        result = await CryptowatchAPI().list_ohlc(
            market="bitflyer",
            product=currency_pair,
            periods=60 * 60 * 24,
            after=close_time,
        )
        result = result[0]
        return schemas.TickerInfo(
            product_common=currency_pair,
            product=exchange_currency_pair,
            exchange="bitflyer",
            close_time=close_time,
            current_time=b_result.timestamp,
            last=b_result.ltp,
            high=result.high_price,
            low=result.low_price,
            volume=result.volume,
            quote_volume=result.quote_volume,
            vwrap=None,
            # volume_by_product: float
            # bid=result.,
            # ask=result.high,
        )

    async def post_order(self, order: Order):
        order = order.copy(deep=True)
        order_dic = self.build_order(order)

        # commission = await api_bitflyer.get_tradingcommission(
        #     product_code=order_dic["product_code"]
        # )

        try:
            result = await api_bitflyer.post_sendchildorder(**order_dic)
        except Exception as e:
            # リクエストが受け付けられない場合は例外が発生
            raise

        # result = {
        #     "child_order_acceptance_id": "xxx"
        # }
        order.order_date = DateTimeAware.utcnow()
        order.result_info = dict(result=result)
        return order

    async def fetch_order_result(self, order: Order):
        order_dic = self.build_order(order)
        try:
            result = await api_bitflyer.get_childorders(
                product_code=order_dic["product_code"],
                child_order_acceptance_id=order.result_info["result"][
                    "child_order_acceptance_id"
                ],
            )
        except Exception as e:
            # リクエストが受け付けられない場合は例外が発生
            raise

        if len(result) == 0:
            return None
        else:
            order.result_info["child_order"] = result
            exec_price, average_price, size, commission = self.calc(result)
            order = OrderResult(
                **order.dict(),
                commission=commission,
                exec_price=exec_price,
            )
            order.price = average_price
            return order

    def calc(self, child_order: dict):
        """
        result = [
            {
                "id": 1111111111,
                "child_order_id": "XXXXXXXXXXXXXXXXXXX",
                "product_code": "FX_BTC_JPY",
                "side": "BUY",
                "child_order_type": "MARKET",
                "price": 0,
                "average_price": 1555487,
                "size": 0.01,
                "child_order_state": "COMPLETED",
                "expire_date": "2020-12-07T23:13:02",
                "child_order_date": "2020-11-07T23:13:02",
                "child_order_acceptance_id": "XXXXXXXXXXXX",
                "outstanding_size": 0,
                "cancel_size": 0,
                "executed_size": 0.01,
                "total_commission": 0
            },
        ]
        """

        if len(child_order) == 0:
            return 0, 0, 0, 0
        else:
            query = Linq(child_order)
            exists_incompleted = query.contains(
                lambda x: x["child_order_state"] != "COMPLETED"
            )
            if exists_incompleted:
                raise Exception()

            commission = query.map(lambda x: x["total_commission"]).sum(
                lambda x: Decimal(str(x))
            )
            exec_price = query.sum(
                lambda x: Decimal(str(x["average_price"])) * Decimal(str(x["size"]))
            )
            size = query.map(lambda x: x["size"]).sum(lambda x: Decimal(str(x)))
            scalar_size = 1 / size
            average_price = exec_price * scalar_size

            return exec_price, average_price, size, commission

    def build_order(self, order: Order):
        currency_pair = self.map_currency_pair(order.currency_pair)
        order_type = order.order_type.upper()
        if order.bid_or_ask == "ask":
            side = "BUY"
        elif order.bid_or_ask == "bid":
            side = "SELL"
        else:
            raise Exception()

        if order_type == "MARKET":
            order_dic = dict(
                product_code=currency_pair,
                child_order_type=order_type,
                side=side,
                size=order.amount,
                time_in_force=order.time_in_force.upper(),
            )
        elif order_type == "LIMIT":
            # テストしてないよ
            raise NotImplementedError()
            # order_dic = dict(
            #     product_code=currency_pair,
            #     child_order_type=order_type,
            #     side=side,
            #     price=order.price,
            #     size=order.amount,
            #     time_in_force=order.time_in_force.upper()
            # )
        else:
            raise Exception()
        return order_dic


@brokers.add
class BackTest(BrokerBase):
    def __init__(self):
        self.date_price = {}

    @staticmethod
    def valid_currency_pair(currency_pair: str) -> bool:
        return True

    @staticmethod
    def map_currency_pair(currency_pair: enums.cryptowatch_currency_pair) -> str:
        return currency_pair

    async def get_topic(self, db, job, close_time_or_every_second):

        from magnet.domain.datastore import crud, models

        m = models.CryptoOhlc
        table = m.as_rep()
        result = crud.get_ticker_one_or_none(
            table.query(db),
            provider=job.provider,
            market=job.market,
            product=job.product,
            periods=job.periods,
            close_time=close_time_or_every_second,
        ).one_or_none()

        if result is None:
            return None

        # self.latest_ticker = result
        self.latest_date = close_time_or_every_second
        self.date_price[close_time_or_every_second] = result.close_price
        return result

    # async def get_ticker(self, currency_pair: str):
    #     return self.latest_ticker

    async def post_order(self, order: Order):
        order = order.copy(deep=True)
        order.order_date = self.latest_date
        order.result_info = dict()
        return order

    async def fetch_order_result(self, order: Order):
        price = self.date_price[order.order_date]
        exec_price = price
        average_price = price
        # size = 1
        commission = 0
        order = OrderResult(
            **order.dict(),
            commission=commission,
            exec_price=exec_price,
        )
        order.price = average_price
        return order

    async def fetch_order_result_for_limit(
        self, order: Order, close_time_or_every_second
    ):
        limit_or_loss = None
        price = self.date_price[close_time_or_every_second]

        if order.limit and order.limit < price:
            limit_or_loss = "limit"

        if order.loss and price < order.loss:
            limit_or_loss = "loss"

        if limit_or_loss is None:
            return None

        price = self.date_price[close_time_or_every_second]
        exec_price = price
        average_price = price
        # size = 1
        commission = 0
        order = OrderResult(
            **order.dict(), commission=commission, exec_price=exec_price
        )
        order.price = average_price
        order.reason = limit_or_loss
        return order
