from decimal import Decimal
from typing import List, Tuple, Union

from fastapi import HTTPException, status
from fastapi.param_functions import Depends
from pydantic import Field, validator
from sqlalchemy.orm import Query

from framework import DateTimeAware
from libs.pydantic.models import BaseModel
from magnet.domain.user.models import User
from pytrade.portfolio import AskBid, PositionStatus, VirtualAccount

from ...commons import intellisense
from ...database import Session
from .models import TradeAccount, TradePosition, TradeVirtualAccount


@intellisense
class CreateAccount(BaseModel):
    user_id: int
    name: str = ""
    version: int = 0
    provider: str = ""
    market: str = ""
    description: str = ""  # 影響なし
    margin: Decimal = Field(0, ge=0, description="証拠金（資金）")

    def do(self, db: Session) -> TradeAccount:
        if not db.query(User).filter(User.id == self.user_id).exists():
            raise Exception(f"user_id={self.user_id}")
        obj = TradeAccount(**self.dict())
        return obj.create(db)


@intellisense
class IndexAccount(BaseModel):
    user_id: int

    def query(self, db: Session) -> "Query[TradeAccount]":
        return db.query(TradeAccount).filter(TradeAccount.user_id == self.user_id)


@intellisense
class GetAccount(BaseModel):
    id: int
    user_id: int

    def do(self, db: Session) -> TradeAccount:
        if not (account := db.query(TradeAccount).get(self.id)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if not account.user_id == self.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return account


@intellisense
class DeleteAccount(BaseModel):
    id: int
    user_id: int

    def do(self, db: Session) -> int:
        account = GetAccount(**self.dict()).do(db)
        return account.delete(db)


@intellisense
class PatchAccount(BaseModel):
    id: int
    user_id: int
    version: int = 0
    provider: str = ""
    market: str = ""
    name: str = ""
    description: str = ""  # 影響なし
    margin: Decimal = Field(0, ge=0, description="証拠金（資金）")

    def do(self, db: Session) -> TradeAccount:
        account = GetAccount(id=self.id, user_id=self.user_id).do(db)
        account.update(db, **self.dict(exclude_unset=True))
        return account


@intellisense
class IndexVirtualAccount(BaseModel):
    user_id: int

    def query(self, db: Session) -> "Query[TradeVirtualAccount]":
        return db.query(TradeVirtualAccount).filter(
            TradeVirtualAccount.user_id == self.user_id
        )


@intellisense
class GetVirtualAccount(BaseModel):
    user_id: int
    id: int

    def do(self, db: Session) -> TradeVirtualAccount:
        if not (account := db.query(VirtualAccount).get(db, id=self.id)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        if not account.user_id == self.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return account


@intellisense
class DeleteVirtualAccount(BaseModel):
    user_id: int
    id: int

    def do(self, db: Session) -> int:
        v_account = GetVirtualAccount(**self.dict()).do(db)
        return v_account.delete(db)


@intellisense
class VirtualAccountCreate(BaseModel):
    user_id: int
    account_id: int
    name: str
    description: str = ""
    product: str = ""
    periods: int = 60 * 60 * 24
    allocation_rate: Decimal = Field(0, ge=0, le=1, description="物理口座内の割合。")
    analyzers: List[str] = []
    decision: str = "default"
    ask_limit_rate: Decimal = Field(None, ge=0)
    ask_loss_rate: Decimal = Field(None, ge=0)
    bid_limit_rate: Decimal = Field(None, ge=0)
    bid_loss_rate: Decimal = Field(None, ge=0)

    def do(self, db: Session) -> TradeVirtualAccount:
        if not db.query(User).filter(User.id == self.user_id).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User not exists."
            )
        if not (account := db.query(TradeAccount).get(self.account_id)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Account not exists."
            )
        obj = TradeAccount(
            **self.dict(), market=account.market, provider=account.provider
        )
        return obj.create(db)


@intellisense
class PatchVirtualAccount(BaseModel):
    id: int
    user_id: int
    # account_id: int
    name: str
    description: str = ""
    product: str = ""
    periods: int = 60 * 60 * 24
    allocation_rate: Decimal = Field(0, ge=0, le=1, description="物理口座内の割合。")
    analyzers: List[str] = []
    decision: str = "default"
    ask_limit_rate: Decimal = Field(None, ge=0)
    ask_loss_rate: Decimal = Field(None, ge=0)
    bid_limit_rate: Decimal = Field(None, ge=0)
    bid_loss_rate: Decimal = Field(None, ge=0)

    def do(self, db: Session) -> TradeVirtualAccount:
        account = GetVirtualAccount(id=self.id, user_id=self.user_id).do(db)
        return account.update(db, **self.dict(exclude_unset=True))


@intellisense
class IndexOrder(BaseModel):
    user_id: int

    def query(self, db: Session) -> "Query[TradePosition]":
        return db.query(TradePosition).filter(TradePosition.user_id == self.user_id)


@intellisense
class GetOrder(BaseModel):
    id: int
    user_id: int


@intellisense
class CreateOrder(BaseModel):
    """
    注文を予約する。apiプロバイダへの発注は別ワーカーが処理し、随時ステータスを更新する。
    監視中の注文は、VirtualAccount.latest_order_idに格納される。
    """

    user_id: int
    trade_account_id: int
    trade_virtual_account_id: int
    entry_order_id: int = None
    is_backtest: bool
    provider: str
    market: str
    product: str
    periods: str
    ask_or_bid: AskBid
    order_price: Decimal
    order_unit: Decimal
    limit_price: Decimal = None
    loss_price: Decimal = None

    @property
    def is_entry(self):
        return self.entry_order_id is not None

    def do(self, db: Session) -> Tuple[TradePosition, TradeVirtualAccount]:
        if not db.query(User).filter(User.id == self.user_id).exists():
            raise Exception(f"user_id={self.user_id}")

        if (
            not db.query(TradeAccount)
            .filter(TradeAccount.id == self.trade_account_id)
            .exists()
        ):
            raise Exception(f"trade_account_id={self.trade_account_id}")

        if (
            not db.query(TradeVirtualAccount)
            .filter(TradeVirtualAccount.id == self.trade_virtual_account_id)
            .exists()
        ):
            raise Exception(f"trade_virtual_account_id={self.trade_virtual_account_id}")

        if self.entry_order_id is not None:
            if (
                not db.query(TradePosition)
                .filter(TradePosition.id == self.entry_order_id)
                .exists()
            ):
                raise Exception(f"entry_order_id={self.entry_order_id}")

        return self.do_no_valid(db)

    def do_no_valid(self, db: Session) -> Tuple[TradePosition, TradeVirtualAccount]:
        """on_createの検証を省いたメソッド。
        例外は開発者が実装ミスなどしない限り発生しない想定なので、
        テストなど限定的な箇所で高速化を図るために使用してよい。
        """
        order = TradePosition(**self.dict(), is_entry=self.is_entry).create(db)
        vaccount = PatchVirtualAccountOnOrderUpdated(
            order_id=order.id,
            user_id=order.user_id,
            trade_virtual_account_id=order.trade_virtual_account_id,
        ).do(db)
        return order, vaccount


@intellisense
class PatchOrderStatusOnRequested(BaseModel):
    """apiプロバイダに発注し、リクエストが受理された時に呼び出す"""

    id: int
    api_data: dict
    order_at: DateTimeAware = Field(default_factory=lambda: DateTimeAware.utcnow)
    status: PositionStatus = Field(PositionStatus.REQUESTED, const=True)

    def do(self, db: Session) -> Tuple[TradePosition, TradeVirtualAccount]:
        order = db.query(TradePosition).get(self.id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        order.update(db, **self.dict())

        vaccount = PatchVirtualAccountOnOrderUpdated(
            order_id=order.id,
            user_id=order.user_id,
            trade_virtual_account_id=order.trade_virtual_account_id,
        ).do(db)
        return order, vaccount


@intellisense
class PatchOrderStatusOnContracted(BaseModel):
    """apiプロバイダから全注文約定が確認できた時に呼び出す"""

    id: int
    api_data: dict
    contract_at: DateTimeAware = Field(default_factory=lambda: DateTimeAware.utcnow)
    contract_price: Decimal
    contract_unit: Decimal
    commission: Decimal
    reason: str
    status: PositionStatus = Field(PositionStatus.CONTRACTED, const=True)

    @validator("api_data")
    def check_api_data(cls, v):
        if not len(v):
            raise ValueError("apiのレスポンスを格納し、状態を追跡可能にしてください。")
        return v

    def do(self, db: Session) -> Tuple[TradePosition, VirtualAccount]:
        order = db.query(TradePosition).get(self.id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        order.update(db, **self.dict())

        vaccount = PatchVirtualAccountOnOrderUpdated(
            order_id=order.id,
            user_id=order.user_id,
            trade_virtual_account_id=order.trade_virtual_account_id,
        ).do(db)

        return order, vaccount


@intellisense
class PatchVirtualAccountOnOrderUpdated(BaseModel):
    """注文更新時に注文と仮想口座との整合性を検証し、仮想口座の最新の注文を更新する"""

    order_id: int
    user_id: int
    trade_virtual_account_id: int

    def do(self, db: Session):

        if not (
            vaccount := db.query(TradeVirtualAccount).get(self.trade_virtual_account_id)
        ):
            raise Exception()

        if vaccount.user_id != self.user_id:
            raise Exception(f"異なるユーザーの注文は更新できません。")

        if vaccount.latest_order_id != self.order_id:
            if vaccount.latest_order_id is not None:
                current_order = db.query(TradePosition).get(vaccount.latest_order_id)
                if not current_order:
                    raise Exception()
                if not current_order.is_completed:
                    raise Exception("監視中の注文が未完了のまま新たな注文を監視することはできません")

        vaccount.update(db, latest_order_id=self.order_id)

        return vaccount
