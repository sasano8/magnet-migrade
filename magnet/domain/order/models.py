from decimal import ROUND_HALF_UP, Decimal

import sqlalchemy as sa

from framework import DateTimeAware
from pytrade.portfolio import AskBid, PositionStatus
from pytrade.stream import BuyAndSellSignal

from ...commons import intellisense
from ...database import Base, Session


@intellisense
class TradeProfile(Base):
    __tablename__ = "trade_profiles"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String(255), nullable=False)
    version = sa.Column(sa.Integer, nullable=False, default=1)
    # is_entry = sa.Column(sa.BOOLEAN, nullable=False)
    # is_backtest = sa.Column(sa.BOOLEAN, nullable=False)
    provider = sa.Column(sa.String(255), nullable=False)  # topic provider
    # broker = sa.Column(sa.String(255), nullable=False)  # marketに対応するブローカ名
    market = sa.Column(sa.String(255), nullable=False)
    product = sa.Column(sa.String(255), nullable=False)
    periods = sa.Column(sa.Integer, nullable=False)
    analyzers = sa.Column(sa.JSON, nullable=False, default=[])
    # status = sa.Column(
    #     sa.Enum(PositionStatus), nullable=False, default=PositionStatus.REQUESTED
    # )
    # ask_or_bid = sa.Column(sa.Enum(AskBid), nullable=False)
    slippage = sa.Column(
        sa.DECIMAL,
        nullable=True,
        comment="バックテストにおいては約定価格のブレを表現し、実際の取引ではショートサーキットのように動作します？？",
        default=Decimal("0.05"),
    )
    # limit_price = sa.Column(sa.DECIMAL, nullable=True, comment="指定価格で利益を確定します。")
    # loss_price = sa.Column(sa.DECIMAL, nullable=True, comment="指定価格で損益を確定します。")
    limit_rate = sa.Column(sa.DECIMAL, nullable=True)
    stop_rate = sa.Column(sa.DECIMAL, nullable=True)

    # order_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    # order_price = sa.Column(sa.DECIMAL, nullable=False)
    # order_unit = sa.Column(sa.DECIMAL, nullable=False)
    # contract_at = sa.Column(
    #     sa.DateTime(timezone=True),
    #     nullable=True,
    #     comment="約定日時。Noneなら約定時に現在日時が入力される。バックテストのため、任意の日付を入力可能",
    # )
    # contract_price = sa.Column(sa.DECIMAL, nullable=True)
    # contract_unit = sa.Column(sa.DECIMAL, nullable=True)
    # profit_loss = sa.Column(sa.DECIMAL, nullable=False, default=0, comment="片方向のオーダー情報しかないので算出不可")
    # commission = sa.Column(sa.DECIMAL, nullable=False, default=0)
    # api_data = sa.Column(sa.JSON, nullable=False, default={})
    # reason = sa.Column(sa.String(255), nullable=False, default="")

    @property
    def is_completed(self):
        if self.status == PositionStatus.CONTRACTED:
            return True
        elif self.status == PositionStatus.CANCELED:
            return True
        else:
            return False


@intellisense
class TradeBot(Base):
    __tablename__ = "trade_bots"
    id = sa.Column(sa.Integer, primary_key=True)
    profile_id = sa.Column(
        sa.Integer,
        sa.ForeignKey(
            "trade_profiles.id",
            onupdate="RESTRICT",
            ondelete="RESTRICT",
        ),
        unique=True,
        nullable=False,
    )
    is_active = sa.Column(sa.Boolean, nullable=False, default=False)

    # 状態を表現するため、基本的にnullableとする
    product_code = sa.Column(sa.String(255), nullable=True)
    entry_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="成行前提でエントリー時に日時を確定させる",
    )
    entry_order = sa.Column(
        sa.JSON, nullable=True, comment="エントリー注文。エントリーは成行で行われ、リミット・ストップ監視まで面倒を見る。"
    )
    entry_order_accepted = sa.Column(sa.JSON, nullable=True)
    entry_order_finalized = sa.Column(sa.JSON, nullable=True)
    entry_cancel_order = sa.Column(
        sa.JSON, nullable=True, comment="リミット・ストップ監視を止めるためのキャンセル注文"
    )
    entry_cancel_order_accepted = sa.Column(sa.JSON, nullable=True)
    entry_cancel_order_finalized = sa.Column(sa.JSON, nullable=True)
    # close_order = sa.Column(sa.JSON, nullable=True)
    # close_order_accepted = sa.Column(sa.JSON, nullable=True)
    # close_order_finalized = sa.Column(sa.JSON, nullable=True)
    # close_cancel_order = sa.Column(sa.JSON, nullable=True)
    # close_cancel_order_accepted = sa.Column(sa.JSON, nullable=True)
    # close_cancel_order_finalized = sa.Column(sa.JSON, nullable=True)
    counter_at = sa.Column(
        sa.DateTime(timezone=True),
        nullable=True,
        comment="成行前提で反対売買時に日時を確定させる。リミット・ストップの場合は、APIによって日時が取れないので認識した日付を入力。",
    )
    counter_order = sa.Column(sa.JSON, nullable=True, comment="残エントリーを決済するための反対売買注文")
    counter_order_accepted = sa.Column(sa.JSON, nullable=True)
    counter_order_finalized = sa.Column(sa.JSON, nullable=True)
    # entry_finalized = sa.Column(sa.JSON, nullable=True)
    # close_finalized = sa.Column(sa.JSON, nullable=True)
    finalized = sa.Column(sa.JSON, nullable=True, comment="entryとcounterの結果をまとめる")

    @property
    def is_empty(self) -> bool:
        return self.entry_order is None

    @property
    def entry_side(self) -> int:
        """エントリーしている場合は、エントリーのサイド（買：1 売り：-1）を返し、エントリーしていない場合は、0を返す"""
        if self.entry_order is None:
            return 0

        return self.entry_order["side"]

    def stmt_reset(self):
        return self.stmt_update(
            # id
            # profile_id
            # is_active
            product_code=None,
            entry_at=None,
            entry_order=None,
            entry_order_accepted=None,
            entry_order_finalized=None,
            entry_cancel_order=None,
            entry_cancel_order_accepted=None,
            entry_cancel_order_finalized=None,
            # close_order=None,
            # close_order_accepted=None,
            # close_order_finalized=None,
            # close_cancel_order=None,
            # close_cancel_order_accepted=None,
            # close_cancel_order_finalized=None,
            # entry_finalized=None,
            # close_finalized=None,
            counter_at=None,
            counter_order=None,
            counter_order_accepted=None,
            counter_order_finalized=None,
            finalized=None,
        )


class TradeLog(Base):
    __tablename__ = "trade_logs"
    id = sa.Column(sa.Integer, primary_key=True)
    profile_id = sa.Column(
        sa.Integer, sa.ForeignKey("trade_profiles.id"), nullable=False
    )
    profile_version = sa.Column(sa.Integer, nullable=False)
    profile_name = sa.Column(sa.String(255), nullable=False)
    is_back_test = sa.Column(sa.Boolean, nullable=False, default=False)
    provider = sa.Column(sa.String(255), nullable=False, default="")
    market = sa.Column(sa.String(255), nullable=False)
    product = sa.Column(sa.String(255), nullable=False)
    periods = sa.Column(sa.Integer, nullable=False)
    side = sa.Column(sa.Integer, nullable=False, comment="エントリーの方向。反対売買は暗黙的にその逆とする。")
    size = sa.Column(sa.DECIMAL, nullable=False)
    entry_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    # entry_side = sa.Column(sa.String(255), nullable=False)
    entry_price = sa.Column(sa.DECIMAL, nullable=False)
    entry_commission = sa.Column(
        sa.DECIMAL, nullable=False, comment="手数料またはボーナス。ボーナスの場合は負数。"
    )
    entry_other_commission = sa.Column(sa.DECIMAL, nullable=False)
    entry_reason = sa.Column(sa.String(255), nullable=False)
    counter_at = sa.Column(sa.DateTime(timezone=True), nullable=False)
    # counter_side = sa.Column(sa.String(255), nullable=False)
    counter_price = sa.Column(sa.DECIMAL, nullable=False)
    counter_commission = sa.Column(sa.DECIMAL, nullable=False)
    counter_other_commission = sa.Column(sa.DECIMAL, nullable=False)
    counter_reason = sa.Column(sa.String(255), nullable=False)

    # properties
    interval_dt = sa.Column(
        sa.Integer, nullable=False, default=0, comment="entryからcounterまでの日数"
    )
    profit = sa.Column(sa.DECIMAL, nullable=False, comment="単純な価格差による損益")
    profit_rate = sa.Column(sa.DECIMAL, nullable=False, comment="単純な価格差による利率")
    fact_profit = sa.Column(sa.DECIMAL, nullable=False, comment="数量と手数料を含んだ実際の損益")
    fact_profit_rate = sa.Column(sa.DECIMAL, nullable=False, comment="数量と手数料を含んだ実際の損益率")

    def update_properties(self):
        self.interval_dt = self.compute_interval_dt(self.entry_at, self.counter_at)
        self.profit = self.compute_profit(
            self.side, self.entry_price, self.counter_price
        )
        self.profit_rate = self.compute_profit_rate(
            self.side, self.entry_price, self.counter_price
        )
        kwargs = dict(
            side=self.side,
            size=self.size,
            entry_price=self.entry_price,
            counter_price=self.counter_price,
            entry_commission=self.entry_commission,
            entry_other_commission=self.entry_other_commission,
            counter_commission=self.counter_commission,
            counter_other_commission=self.counter_other_commission,
        )

        self.fact_profit = self.compute_fact_profit(**kwargs)
        self.fact_profit_rate = self.compute_fact_profit_rate(**kwargs)

    @staticmethod
    def compute_interval_dt(entry_dt: DateTimeAware, counter_dt: DateTimeAware) -> int:
        time_delta = counter_dt - entry_dt
        return time_delta.days

    @staticmethod
    def compute_profit(side, entry_price, counter_price):
        if side == 1:
            return counter_price - entry_price
        elif side == -1:
            return entry_price - counter_price
        else:
            raise Exception()

    @staticmethod
    def compute_profit_rate(side, entry_price: Decimal, counter_price: Decimal):
        if side == 1:
            rate = counter_price / entry_price
        elif side == -1:
            rate = entry_price / counter_price
        else:
            raise Exception()

        return rate.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def compute_fact_profit(
        cls,
        side,
        size,
        entry_price: Decimal,
        counter_price: Decimal,
        entry_commission,
        entry_other_commission,
        counter_commission,
        counter_other_commission,
    ):
        profit = cls.compute_profit(side, entry_price * size, counter_price * size)
        return profit + (
            -entry_commission
            - entry_other_commission
            - counter_commission
            - counter_other_commission
        )

    @classmethod
    def compute_fact_profit_rate(
        cls,
        side,
        size,
        entry_price: Decimal,
        counter_price: Decimal,
        entry_commission,
        entry_other_commission,
        counter_commission,
        counter_other_commission,
    ):
        profit = cls.compute_fact_profit(
            side,
            size,
            entry_price,
            counter_price,
            entry_commission,
            entry_other_commission,
            counter_commission,
            counter_other_commission,
        )

        entry_amount = entry_price * size
        close_amount = entry_amount + profit
        return close_amount / entry_amount
