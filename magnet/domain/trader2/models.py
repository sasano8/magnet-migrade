from __future__ import annotations

from decimal import Decimal

import sqlalchemy as sa
from sqlalchemy.orm import relationship

from pytrade.portfolio import AskBid, PositionStatus
from pytrade.properties import TradePositionProperty

from ...database import Base


class TradePosition(Base, TradePositionProperty):
    __tablename__ = "trade_order"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="アクティブな注文などがあるため、RESTRICTとする。（現在はめんどいのでCASCADE）",
    )
    trade_account_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("trade_account.id", ondelete="CASCADE"),
        nullable=False,
        comment="アクティブな注文などがあるため、RESTRICTとする。（現在はめんどいのでCASCADE）",
    )
    trade_virtual_account_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("trade_virtual_account.id", ondelete="CASCADE"),
        nullable=False,
        comment="アクティブな注文などがあるため、RESTRICTとする。（現在はめんどいのでCASCADE）",
    )
    entry_order_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("trade_order.id"),
        nullable=True,
        comment="エントリーとなったorder.id　エントリーの時はNoneとなり、これで一連の流れを表現する",
    )
    is_entry = sa.Column(sa.BOOLEAN, nullable=False)
    is_backtest = sa.Column(sa.BOOLEAN, nullable=False)
    provider = sa.Column(sa.String(255), nullable=False)
    market = sa.Column(sa.String(255), nullable=False)
    product = sa.Column(sa.String(255), nullable=False)
    periods = sa.Column(sa.Integer, nullable=False)
    status = sa.Column(
        sa.Enum(PositionStatus), nullable=False, default=PositionStatus.REQUESTED
    )
    ask_or_bid = sa.Column(sa.Enum(AskBid), nullable=False)
    slippage = sa.Column(
        sa.DECIMAL,
        nullable=True,
        comment="バックテストにおいては約定価格のブレを表現し、実際の取引ではショートサーキットのように動作します？？",
        default=Decimal("0.05"),
    )
    limit_price = sa.Column(sa.DECIMAL, nullable=True, comment="指定価格で利益を確定します。")
    loss_price = sa.Column(sa.DECIMAL, nullable=True, comment="指定価格で損益を確定します。")
    order_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    order_price = sa.Column(sa.DECIMAL, nullable=False)
    order_unit = sa.Column(sa.DECIMAL, nullable=False)
    contract_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="約定日時。Noneなら約定時に現在日時が入力される。バックテストのため、任意の日付を入力可能",
    )
    contract_price = sa.Column(sa.DECIMAL, nullable=True)
    contract_unit = sa.Column(sa.DECIMAL, nullable=True)
    # profit_loss = sa.Column(sa.DECIMAL, nullable=False, default=0, comment="片方向のオーダー情報しかないので算出不可")
    commission = sa.Column(sa.DECIMAL, nullable=False, default=0)
    api_data = sa.Column(sa.JSON, nullable=False, default={})
    reason = sa.Column(sa.String(255), nullable=False, default="")

    @property
    def is_completed(self):
        if self.status == PositionStatus.CONTRACTED:
            return True
        elif self.status == PositionStatus.CANCELED:
            return True
        else:
            return False


class TradeVirtualAccount(Base):
    __tablename__ = "trade_virtual_account"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    trade_account_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("trade_account.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = sa.Column(sa.Integer, nullable=False, default=0)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(1024), nullable=False, default="")
    product = sa.Column(sa.String(255), nullable=False)
    periods = sa.Column(sa.Integer, nullable=False, default=1)
    allocated_margin = sa.Column(sa.DECIMAL, nullable=False, default=0)
    allocation_rate = sa.Column(sa.DECIMAL, nullable=False, default=0)
    ask_limit_rate = sa.Column(sa.DECIMAL, nullable=True)
    ask_loss_rate = sa.Column(sa.DECIMAL, nullable=True)
    bid_limit_rate = sa.Column(sa.DECIMAL, nullable=True)
    bid_loss_rate = sa.Column(sa.DECIMAL, nullable=True)
    latest_order_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("trade_order.id"),
        nullable=True,
    )
    # position = sa.Column(sa.JSON, nullable=True)

    __table_args__ = (sa.UniqueConstraint("user_id", "name"),)  # 同一ユーザーの同名仮想アカウントは許可しない


class TradeAccount(Base):
    __tablename__ = "trade_account"
    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    version = sa.Column(sa.Integer, nullable=False, default=0)
    name = sa.Column(sa.String(255), nullable=False)
    description = sa.Column(sa.String(1024), nullable=False)
    provider = sa.Column(sa.String(255), nullable=False)
    market = sa.Column(sa.String(255), nullable=False)
    margin = sa.Column(sa.DECIMAL, nullable=False, default=0)
    # accounts = sa.Column(sa.JSON, nullable=False, default=[])
    accounts = relationship("TradeVirtualAccount")
