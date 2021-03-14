import datetime
from typing import NamedTuple

from sqlalchemy.orm import Session

from framework import DateTimeAware, Linq

from ..commons import BulkResult
from ..domain.datastore import models, schemas
from .__main__ import daily


@daily
async def daily_update_crypto_pair(db: Session) -> BulkResult:
    """
    指定した条件のデータを削除した後、指定したデータを登録する。（洗い替え方式）
    戻り値に削除件数と登録件数を返す。
    """
    from ..trade_api.exchanges.cryptowatch import CryptowatchAPI

    m = models.CryptoPairs
    rep = m.as_rep()
    provider = "cryptowatch"

    # extract
    data = await CryptowatchAPI().get_pairs()

    # transform
    query = (
        Linq(data)
        .map(lambda x: schemas.Pairs(provider=provider, symbol=x.symbol).dict())  # type: ignore
        .map(lambda x: m(**x))
    )

    # load
    deleted = rep.query(db).filter(m.provider == provider).delete()

    count, succeeded, exceptions = query.dispatch(db.add)
    if exceptions:
        raise Exception(exceptions)

    return BulkResult(deleted=deleted, inserted=succeeded, errors=exceptions)


@daily
async def daily_update_crypto_ohlc(db: Session) -> BulkResult:
    """指定したリソースの４本値を洗い替えする"""
    from ..trade_api.exchanges.cryptowatch import CryptowatchAPI

    class Partition(NamedTuple):
        provider: str = "cryptowatch"
        market: str = "bitflyer"
        product: str = "btcjpy"
        periods: int = 60 * 60 * 24

    partition = Partition()

    after: DateTimeAware = DateTimeAware(2010, 1, 1)

    # extract
    data = await CryptowatchAPI().list_ohlc(
        market=partition.market,
        product=partition.product,
        periods=partition.periods,
        after=after,
    )

    diff = datetime.timedelta(days=-1)
    # transform
    query = Linq(data).map(
        lambda x: schemas.Ohlc(
            **partition._asdict(),  # type: ignore
            close_time=x.close_time,
            start_time=x.close_time + diff,
            open_price=x.open_price,
            high_price=x.high_price,
            low_price=x.low_price,
            close_price=x.close_price,
            volume=x.volume,
            quote_volume=x.quote_volume,
        )
    )

    # analyze
    it = schemas.Ohlc.compute_technical(query)

    # load
    m = models.CryptoOhlc
    rep = m.as_rep()

    deleted = (
        # crud.query_partition(db, **partition._asdict())
        rep.query(db)
        .filter(
            m.provider == partition.provider,
            m.market == partition.market,
            m.product == partition.product,
            m.periods == partition.periods,
        )
        .filter(m.close_time >= after)
        .delete()
    )

    count, succeeded, exceptions = (
        Linq(it).map(lambda x: m(**x.dict())).dispatch(lambda x: db.add(x))
    )
    if exceptions:
        raise Exception(exceptions)

    return BulkResult(deleted=deleted, inserted=succeeded, errors=exceptions)
