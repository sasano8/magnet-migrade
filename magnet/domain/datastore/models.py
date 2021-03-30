import datetime
from typing import Iterator, Literal

import sqlalchemy as sa
from sqlalchemy.orm import Query

from framework import DateTimeAware

from ...database import Base, Session


class CryptoPair(Base):
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
    """外部データソースから取得したチャート"""

    open_time = sa.Column(sa.Date, nullable=True)
    close_time = sa.Column(sa.Date, nullable=False)
    open_price = sa.Column(sa.Float, nullable=False)
    high_price = sa.Column(sa.Float, nullable=False)
    low_price = sa.Column(sa.Float, nullable=False)
    close_price = sa.Column(sa.Float, nullable=False)
    volume = sa.Column(sa.Float, nullable=False)
    quote_volume = sa.Column(sa.Float, nullable=False)

    wb_cs = sa.Column(
        sa.DECIMAL, nullable=False, default=0, comment="white black candle stick"
    )
    wb_cs_rate = sa.Column(
        sa.DECIMAL, nullable=False, default=0, comment="white black candle stick"
    )
    t_sma_5 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_10 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_15 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_20 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_25 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_30 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_200 = sa.Column(sa.Float, nullable=False, default=0)
    t_sma_rate = sa.Column(sa.DECIMAL(10, 2), nullable=False, default=0)
    t_cross = sa.Column(
        sa.Integer,
        nullable=False,
        default=0,
        comment="1=golden cross -1=dead cross 2021/3/15 t_sma_5 t_sma_25のクロスを検出",
    )
    t_rsi_14 = sa.Column(sa.DECIMAL, nullable=True, default=0)

    __table_args__ = (
        sa.UniqueConstraint("provider", "market", "product", "periods", "close_time"),
        sa.Index("uix_query", "provider", "market", "product", "periods"),
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
    pass


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


class EtlJobResult(Base):
    id = sa.Column(sa.Integer, primary_key=True)
    execute_at = sa.Column(
        sa.DateTime(timezone=True), nullable=False, default=DateTimeAware.utcnow
    )
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(1023), nullable=False, default="")
    deleted = sa.Column(sa.Integer, nullable=False)
    inserted = sa.Column(sa.Integer, nullable=False)
    ignored = sa.Column(sa.Integer, nullable=False, default=0)
    errors = sa.Column(sa.JSON, nullable=False, default=[])
    error_summary = sa.Column(sa.Text, nullable=False)
    warning = sa.Column(sa.Text, nullable=False)
