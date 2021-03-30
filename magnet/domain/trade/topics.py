from datetime import date, timedelta
from functools import partial

from sqlalchemy.sql import text

from framework import DateTimeAware

from ...database import get_db
from ..datastore.models import CryptoOhlc
from ..datastore.schemas import Ohlc
from .abc import TopicProvider
from .repository import TopicRepository


@TopicRepository.register
class CurrentTickerTestProvider(TopicProvider):
    """テスト用の現在の板情報を取得する"""

    _name = "test_current_ticker"

    # def __post_init__(self):
    #     self._get_topic = partial(self.broker.get_ticker, self.worker.product)
    @classmethod
    def get_alias(cls):
        return "current_ticker"

    async def get_topic(self, current_dt):
        # return await self._get_topic()
        raise NotImplementedError()


@TopicRepository.register
class CurrentTickerProvider(TopicProvider):
    """現在の板情報を取得する"""

    _name = "current_ticker"

    def __post_init__(self):
        mapping = {"btcfxjpy": "FX_BTC_JPY"}
        product = mapping.get(self.profile.product)
        self._get_topic = partial(self.broker.get_ticker, product)

    async def get_topic(self, current_dt):
        return await self._get_topic()


@TopicRepository.register
class YesterdayOhlcProvider(TopicProvider):
    """前日の分析済みOHLCを取得する"""

    _name = "yesterday_ohlc"

    def __post_init__(self):
        self._sql = text(
            f"SELECT * FROM {CryptoOhlc.__tablename__} where open_time = :open_time"
        )

    async def get_topic(self, current_dt: DateTimeAware):
        yesterday = date(current_dt.year, current_dt.month, current_dt.day) - timedelta(
            days=1
        )
        p = self.profile
        for db in get_db():
            stmt = db.query(CryptoOhlc).filter(
                CryptoOhlc.provider == p.provider,
                CryptoOhlc.market == p.market,
                CryptoOhlc.product == p.product,
                CryptoOhlc.periods == p.periods,
                CryptoOhlc.open_time == yesterday,
            )
            yesterday_ohlc = stmt.one_or_none()
            if yesterday_ohlc is None:
                return None
            else:
                return Ohlc.from_orm(yesterday_ohlc)
