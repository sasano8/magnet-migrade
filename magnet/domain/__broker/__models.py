import sqlalchemy as sa
from sqlalchemy.orm import query

from ...database import Base

# class TradeProfileBase:
#     id = sa.Column(sa.Integer, primary_key=True)
#     version = sa.Column(sa.Integer, nullable=False, default=0)
#     name = sa.Column(sa.String(255), nullable=False)
#     description = sa.Column(sa.String(1024), nullable=False)
#     provider = sa.Column(sa.String(255), nullable=False)
#     market = sa.Column(sa.String(255), nullable=False)
#     product = sa.Column(sa.String(255), nullable=False)
#     periods = sa.Column(sa.Integer, nullable=False)
#     cron = sa.Column(sa.String(255), nullable=False)
#     broker = sa.Column(sa.String(255), nullable=False)
#     bet_strategy = sa.Column(sa.String(255), nullable=True)
#     order_logic = trade_rule = sa.Column(sa.JSON, nullable=True, default={})
#     job_type = sa.Column(sa.String(255), nullable=True)
#     trade_type = sa.Column(sa.String(255), nullable=False)
#     monitor_topic = sa.Column(sa.String(255), nullable=False)
#     detector_name = sa.Column(sa.String(255), nullable=False)

#     @declared_attr
#     def __table_args__(cls):
#         return (sa.UniqueConstraint("name"),)


# class TradeProfile(TradeProfileBase, Base):
#     __tablename__ = "trade_profile"


# class TradeJob(TradeProfileBase, Base):
#     __tablename__ = "trade_job"
#     last_check_date = sa.Column(sa.DateTime(timezone=True), nullable=True)
#     order_status = sa.Column(sa.JSON, nullable=True)


class TradeOrder(Base):
    __tablename__ = "tradeorder"
    id = sa.Column(sa.Integer, primary_key=True)
    broker = sa.Column(sa.String(1024), nullable=False, default="test")
    description = sa.Column(sa.String(1024), nullable=False)
    provider = sa.Column(sa.String(255), nullable=False)
    market = sa.Column(sa.String(255), nullable=False)
    product = sa.Column(sa.String(255), nullable=False)
    order_at = sa.Column(
        sa.DateTime(timezone=True), nullable=True, comment="apiが注文を受け付けた日付"
    )
    order_id = sa.Column(sa.String(255), nullable=True, comment="apiから発行される外部id")
    bid_or_ask = sa.Column(sa.String(255), nullable=True, comment="apiから発行される外部id")
    order_type = sa.Column(sa.String(255), nullable=False)
    kwargs = sa.Column(sa.JSON, nullable=False, default={})
