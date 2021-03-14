import datetime
from typing import Iterator, Literal

import sqlalchemy as sa
from sqlalchemy.orm import Query

from framework import DateTimeAware

from ...database import Base, Session


class CryptoPairs(Base):
    __tablename__ = "__crypto_pairs"
    id = sa.Column(sa.Integer, primary_key=True)
    provider = sa.Column(sa.String(255), nullable=False, default="")
    symbol = sa.Column(sa.String(255), nullable=False, unique=True)


class CryptoBase:
    id = sa.Column(sa.Integer, primary_key=True)
    provider = sa.Column(sa.String(255), nullable=False, default="")
    market = sa.Column(sa.String(255), nullable=False)
    product = sa.Column(sa.String(255), nullable=False)
    periods = sa.Column(sa.Integer, nullable=False)


class CryptoOhlc(Base, CryptoBase):
    __tablename__ = "__crypto_ohlc_daily"
    close_time = sa.Column(sa.Date, nullable=False)
    start_time = sa.Column(sa.Date, nullable=True)
    open_price = sa.Column(sa.Float, nullable=False)
    high_price = sa.Column(sa.Float, nullable=False)
    low_price = sa.Column(sa.Float, nullable=False)
    close_price = sa.Column(sa.Float, nullable=False)
    volume = sa.Column(sa.Float, nullable=False)
    quote_volume = sa.Column(sa.Float, nullable=False)

    t_sma_5 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_10 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_15 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_20 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_25 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_30 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_200 = sa.Column(sa.Float, nullable=False, default=0)
    t_cross = sa.Column(
        sa.Integer, nullable=False, default=0, comment="1=golden cross -1=dead cross"
    )

    __table_args__ = (
        sa.UniqueConstraint("provider", "market", "product", "periods", "close_time"),
        sa.Index("uix_query", "provider", "market", "product", "periods"),
        {"comment": "外部データソースから取得したチャート"},
    )

    @classmethod
    def Q_select_start_time(
        cls,
        db: Session,
        *,
        provider: str,
        market: str,
        product: str,
        periods: int,
        after: DateTimeAware = DateTimeAware(2010, 1, 1),
        until: datetime.date = None,
        order_by: Literal["asc", "desc"] = "asc",
    ) -> Iterator[DateTimeAware]:
        """指定した領域内の日付を返す。"""
        if provider != "cryptowatch":
            raise ValueError()

        if periods != 60 * 60 * 24:
            raise ValueError()

        if order_by == "asc":
            sort = cls.start_time.asc()
        elif order_by == "desc":
            sort = cls.start_time.desc()
        else:
            raise ValueError()

        query = db.query(cls.start_time).filter(
            cls.provider == provider,
            cls.market == market,
            cls.product == product,
            cls.periods == 60 * 60 * 24,
            cls.start_time >= after,
        )
        if until is not None:
            query = query.filter(cls.start_time < until)

        def date_to_datetime(dt):
            return DateTimeAware.combine(dt, DateTimeAware.min.time())

        return (date_to_datetime(x.start_time) for x in query.order_by(sort))

    # TODO: closetimeは難しいのでstart_timeに移植して削除する
    @classmethod
    def Q_select_close_date_range(
        cls,
        db: Session,
        # query: "Query[models.CryptoOhlc]",
        provider: str,
        market: str,
        product: str,
        periods: str,
        after: DateTimeAware = DateTimeAware(2010, 1, 1),
        until: datetime.date = None,
        order_by: Literal["asc", "desc"] = "asc",
    ) -> "Query[CryptoOhlc]":
        # m = models.CryptoOhlc
        if order_by == "asc":
            sort = cls.close_time.asc()
        elif order_by == "desc":
            sort = cls.close_time.desc()
        else:
            raise Exception()

        query = db.query(cls).filter(
            cls.provider == provider,
            cls.market == market,
            cls.product == product,
            cls.periods == periods,
            cls.close_time >= after,
        )
        if until is not None:
            query = query.filter(cls.close_time <= until)
        return query.order_by(sort)


class CryptoTradeResult(Base, CryptoBase):
    __tablename__ = "crypto_trade_results"
    size = sa.Column(sa.DECIMAL, nullable=False)
    ask_or_bid = sa.Column(sa.Integer, nullable=False)
    entry_date = sa.Column(sa.DateTime(timezone=True), nullable=False)
    entry_close_date = sa.Column(sa.DateTime(timezone=True), nullable=False)
    entry_side = sa.Column(sa.String(255), nullable=False)
    entry_price = sa.Column(sa.DECIMAL, nullable=False)
    entry_commission = sa.Column(sa.DECIMAL, nullable=False)
    entry_reason = sa.Column(sa.String(255), nullable=False)
    settle_date = sa.Column(sa.DateTime(timezone=True), nullable=False)
    settle_close_date = sa.Column(sa.DateTime(timezone=True), nullable=False)
    settle_side = sa.Column(sa.String(255), nullable=False)
    settle_price = sa.Column(sa.DECIMAL, nullable=False)
    settle_commission = sa.Column(sa.DECIMAL, nullable=False)
    settle_reason = sa.Column(sa.String(255), nullable=False)
    job_name = sa.Column(sa.String(255), nullable=False)
    job_version = sa.Column(sa.String(255), nullable=False)
    is_back_test = sa.Column(sa.Boolean, nullable=False, default=False)
    close_date_interval = sa.Column(sa.Integer, nullable=False)
    diff_profit = sa.Column(sa.DECIMAL, nullable=False)
    diff_profit_rate = sa.Column(sa.DECIMAL, nullable=False)
    fact_profit = sa.Column(sa.DECIMAL, nullable=False)

    @classmethod
    def P_delete_by_job_name(cls, db: Session, job_name: str) -> int:
        return db.query(cls).filter(cls.job_name == job_name).delete()


class WebArchiveBase:
    id = sa.Column(sa.Integer, primary_key=True)
    referer = sa.Column(sa.String(1023), nullable=True)
    url = sa.Column(sa.String(1023), nullable=True)
    url_cache = sa.Column(sa.String(1023), nullable=True)
    title = sa.Column(sa.String(1023), nullable=True, default="")
    summary = sa.Column(sa.String(1023), nullable=True, default="")
    memo = sa.Column(sa.String(1023), nullable=False, default="")
    detail = sa.Column(sa.JSON, nullable=False, default={})


class Topic(Base, WebArchiveBase):
    __tablename__ = "__topic"


# https://news.livedoor.com/article/detail/18946401/
# コロナにより観光客が減ったため、奈良の鹿が鹿センベイを食べずにやせ細っている


# class Thread(Base, WebArchiveBase):
#     __tablename__ = "thread"


# class DataSource(Base, WebArchiveBase):
#     __tablename__ = "__datasource"
#     id = sa.Column(sa.Integer, primary_key=True, index=True)
#     url = sa.Column(sa.String(1023), nullable=True)
#     url_cache = sa.Column(sa.String(1023), nullable=True)
#     title = sa.Column(sa.String(1023), nullable=True, default="")
#     summary = sa.Column(sa.String(1023), nullable=True, default="")
#     memo = sa.Column(sa.String(1023), nullable=False, default="")
#     detail = sa.Column(sa.JSON, nullable=False, default={})

# url = "http://www.scj.go.jp/ja/info/kohyo/year.html"  # 日本学術会議　提言　報告
