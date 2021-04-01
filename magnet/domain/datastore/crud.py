import datetime
from typing import Literal, TypeVar

from sqlalchemy.orm import Query

from framework import DateTimeAware

from . import models

T = TypeVar("T")


def filter_partition(
    query: "Query[models.CryptoOhlc]",
    provider: str,
    market: str,
    product: str,
    periods: str,
) -> "Query[models.CryptoOhlc]":
    return query.filter(
        models.CryptoOhlc.provider == provider,
        models.CryptoOhlc.market == market,
        models.CryptoOhlc.product == product,
        models.CryptoOhlc.periods == periods,
        # m.close_time >= after,
    )


def get_ticker_one_or_none(
    query: "Query[models.CryptoOhlc]",
    provider: str,
    market: str,
    product: str,
    periods: str,
    close_time: datetime.date,
) -> "Query[models.CryptoOhlc]":
    m = models.CryptoOhlc
    return query.filter(
        m.provider == provider,
        m.market == market,
        m.product == product,
        m.periods == periods,
        m.close_time == close_time,
    )


# TODO: 普通にquery作ればよくね？？　一箇所に集められるのは、一応メリットか、、、
def select_close_date_range(
    query: "Query[models.CryptoOhlc]",
    provider: str,
    market: str,
    product: str,
    periods: str,
    after: DateTimeAware = DateTimeAware(2010, 1, 1),
    until: datetime.date = None,
    order_by: Literal["asc", "desc"] = "asc",
) -> "Query[models.CryptoOhlc]":
    m = models.CryptoOhlc
    if order_by == "asc":
        sort = m.close_time.asc()
    elif order_by == "desc":
        sort = m.close_time.desc()
    else:
        raise Exception()
    query.filter(
        m.provider == provider,
        m.market == market,
        m.product == product,
        m.periods == periods,
        m.close_time >= after,
        m.close_time <= until,
    ).order_by(sort)
    return query
