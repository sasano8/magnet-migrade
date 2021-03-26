import datetime
from typing import Literal

from sqlalchemy.orm import Session

from framework import DateTimeAware, Linq

from ..commons import BaseModel, BulkResult
from ..domain.datastore import models, schemas
from .executor import daily


@daily
async def daily_update_crypto_pair(db: Session) -> BulkResult:
    """
    指定した条件のデータを削除した後、指定したデータを登録する。（洗い替え方式）
    戻り値に削除件数と登録件数を返す。
    """
    from ..trade_api.exchanges.cryptowatch import CryptowatchAPI

    m = models.CryptoPairs
    provider = "cryptowatch"

    # extract
    data = await CryptowatchAPI().get_pairs()

    # transform
    query = (
        Linq(data)
        # .map(lambda x: schemas.Pairs(provider=provider, symbol=x.symbol).dict())  # type: ignore
        .map(lambda x: m(provider=provider, symbol=x.symbol))
    )

    # load
    deleted = db.query(m).filter(m.provider == provider).delete()

    count, succeeded, exceptions = query.dispatch(db.add)
    if exceptions:
        raise Exception(exceptions)

    return BulkResult(deleted=deleted, inserted=succeeded, errors=exceptions)


class JobBase(BaseModel):
    @property
    def description(self):
        return self.__class__.__doc__ or ""


class CryptoWatchOhlcExtractor(JobBase):
    """指定し市場通過ピリオドをcryptowatchから取得し、データストアに保存する。"""

    provider: Literal["cryptowatch"]
    market: Literal["bitflyer"]
    product: Literal["btcjpy", "btcfxjpy"]
    periods: int
    after: DateTimeAware = DateTimeAware(2010, 1, 1)

    @property
    def description(self):
        return f"{self.provider} {self.market} {self.product} {self.periods}"

    async def __call__(self, db: Session) -> BulkResult:
        from ..trade_api.exchanges.cryptowatch import CryptowatchAPI

        data = await CryptowatchAPI().list_ohlc(
            market=self.market,
            product=self.product,
            periods=self.periods,
            after=self.after,
        )

        diff = datetime.timedelta(days=-1)
        partition = self.dict(exclude={"after"})
        # transform
        query = Linq(data).map(
            lambda x: schemas.Ohlc(
                **partition,  # type: ignore
                close_time=x.close_time,
                open_time=x.close_time + diff,
                open_price=x.open_price,
                high_price=x.high_price,
                low_price=x.low_price,
                close_price=x.close_price,
                volume=x.volume,
                quote_volume=x.quote_volume,
            )
        )

        # analyze
        it = schemas.Ohlc.compute_sma_and_cross(query)
        it = schemas.Ohlc.compute_wb_cs(it)
        it = schemas.Ohlc.compute_rsi(it)

        # load
        m = models.CryptoOhlc

        deleted = (
            db.query(models.CryptoOhlc)
            .filter(
                m.provider == self.provider,
                m.market == self.market,
                m.product == self.product,
                m.periods == self.periods,
            )
            .filter(m.close_time >= self.after)
            .delete()
        )

        count, succeeded, exceptions = (
            Linq(it).map(lambda x: m(**x.dict())).dispatch(lambda x: db.add(x))
        )
        db.flush()
        ignored = db.query(models.CryptoOhlc).filter(m.close_price == 0).delete()
        warning = f"終値0円は不正なレコードとして無視されました" if ignored else ""

        if exceptions:
            raise Exception(exceptions)

        return BulkResult(
            deleted=deleted,
            inserted=succeeded - ignored,
            ignored=ignored,
            errors=exceptions,
            warning=warning,
        )


class SystemTradeBot(JobBase):
    """test用bot"""

    profile_id: int

    async def __call__(self, db: Session) -> BulkResult:
        from magnet.domain.order.usecase import ScheduleBot

        errors = []

        try:
            await ScheduleBot(profile_id=self.profile_id).deal(db)
        except Exception as e:
            errors.append(e)

        return BulkResult(errors=errors)


daily(
    CryptoWatchOhlcExtractor(
        provider="cryptowatch",
        market="bitflyer",
        product="btcjpy",
        periods=60 * 60 * 24,
        after=DateTimeAware(2010, 1, 1),
    )
)


daily(
    CryptoWatchOhlcExtractor(
        provider="cryptowatch",
        market="bitflyer",
        product="btcfxjpy",
        periods=60 * 60 * 24,
        after=DateTimeAware(2010, 1, 1),
    )
)

daily(SystemTradeBot(profile_id=1))
