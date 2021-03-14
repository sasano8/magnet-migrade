from __future__ import annotations

from typing import Union

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Query

from ...database import Base, Session


class TradeDetector(Base):
    __tablename__ = "trade_detector"

    id = sa.Column(sa.Integer, primary_key=True)
    is_system = sa.Column(sa.Boolean, nullable=False, default=False)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(1023), nullable=False)
    code = sa.Column(sa.Text, nullable=False, default="")
    invert_ask_or_bid = sa.Column(
        sa.Boolean, nullable=False, default=False, comment="ask bidのフラグを反転させます。"
    )


class TradeProfileBase:
    id = sa.Column(sa.Integer, primary_key=True)
    version = sa.Column(sa.Integer, nullable=False, default=0)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(1024), nullable=False)
    provider = sa.Column(sa.String(255), nullable=False)
    market = sa.Column(sa.String(255), nullable=False)
    product = sa.Column(sa.String(255), nullable=False)
    periods = sa.Column(sa.Integer, nullable=False)
    cron = sa.Column(sa.String(255), nullable=False)
    broker = sa.Column(sa.String(255), nullable=False)
    bet_strategy = sa.Column(sa.String(255), nullable=True)
    order_logic = trade_rule = sa.Column(sa.JSON, nullable=True, default={})
    job_type = sa.Column(sa.String(255), nullable=True)
    trade_type = sa.Column(sa.String(255), nullable=False)
    monitor_topic = sa.Column(sa.String(255), nullable=False)
    detector_name = sa.Column(sa.String(255), nullable=False)

    @declared_attr
    def __table_args__(cls):
        return (sa.UniqueConstraint("name"),)


class TradeProfile(TradeProfileBase, Base):
    __tablename__ = "trade_profile"

    @classmethod
    def Q_get_by_name(cls, db: Session, *, name: str) -> Union[TradeProfile, None]:
        return cls.as_rep().query(db).filter(cls.name == name).one_or_none()


class TradeJob(TradeProfileBase, Base):
    __tablename__ = "trade_job"
    last_check_date = sa.Column(sa.DateTime(timezone=True), nullable=True)
    order_status = sa.Column(sa.JSON, nullable=True)

    @classmethod
    def Q_get_by_name(cls, db: Session, *, name: str) -> Union[TradeJob, None]:
        return cls.as_rep().query(db).filter(cls.name == name).one_or_none()

    @classmethod
    def Q_get_workers(
        cls, db: Session, *, id: int = None, job_type: str = None
    ) -> "Query[TradeJob]":
        query = db.query(cls)
        if id is not None:
            query = query.filter(cls.id == id)

        if job_type is not None:
            query = query.filter(cls.job_type == job_type)

        return query
