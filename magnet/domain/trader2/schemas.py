import enum
from dataclasses import dataclass
from decimal import Decimal
from functools import wraps
from typing import Any, Callable, List, Type, TypeVar, no_type_check_decorator

from pydantic import root_validator, validator
from pydantic.fields import Field

from framework import DateTimeAware
from magnet.database import Base
from pytrade.portfolio import Account as _a
from pytrade.portfolio import AskBid, Portfolio, PositionStatus
from pytrade.portfolio import TradePosition as _p
from pytrade.portfolio import VirtualAccount as _v
from pytrade.properties import TradePositionProperty

from ...commons import BaseModel


class OrderCreate(BaseModel):
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

    @root_validator
    def check_entry(cls, values):
        is_entry = values.get("is_entry")
        entry_order_id = values.get("entry_order_id")
        if is_entry and entry_order_id is None:
            pass
        elif not is_entry and entry_order_id:
            pass
        else:
            raise ValueError(f"{is_entry=} {entry_order_id=}")
        return values


class OrderRequested(BaseModel):
    id: int
    api_data: dict
    order_at: DateTimeAware = Field(default_factory=lambda: DateTimeAware.utcnow)
    status: PositionStatus = Field(PositionStatus.REQUESTED, const=True)

    @validator("api_data")
    def check_api_data(cls, v):
        if not len(v):
            raise ValueError("apiのレスポンスを格納し、状態を追跡可能にしてください。")
        return v


class OrderContracted(BaseModel):
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


class TradePosition(_p):
    pass


class TradeVirtualAccount(_v):
    class Config:
        # orm_mode = True
        schema_extra = {
            "example": {
                "name": "仮想口座１",
                "allocation_rate": 0,
                "allocated_margin": 0,
                "product": "btcjpy",
                "periods": 86400,
                "ask_limit_rate": 1.14,
                "ask_loss_rate": 1.05,
                "bid_limit_rate": 1.14,
                "bid_loss_rate": 1.05,
            }
        }


class TradeAccount(_a):
    class Config:
        # orm_mode = True
        schema_extra = {
            "example": {
                "name": "物理口座１",
                "version": 0,
                "provider": "cryptowatch",
                "market": "bitflyer",
                "description": "",
                "margin": 0,
            }
        }


class Account(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str = ""
    version: int = 0
    provider: str = ""
    market: str = ""
    description: str = ""  # 影響なし
    margin: Decimal = Field(0, ge=0, description="証拠金（資金）")


class AccountCreate(BaseModel):
    user_id: int
    name: str = ""
    version: int = 0
    provider: str = ""
    market: str = ""
    description: str = ""  # 影響なし
    margin: Decimal = Field(0, ge=0, description="証拠金（資金）")

    class Config:
        schema_extra = {
            "example": {
                "name": "物理口座１",
                "version": 0,
                "provider": "cryptowatch",
                "market": "bitflyer",
                "description": "",
                "margin": 0,
            }
        }


class AccountPatch(BaseModel):
    id: int
    user_id: int
    version: int = 0
    provider: str = ""
    market: str = ""
    name: str = ""
    description: str = ""  # 影響なし
    margin: Decimal = Field(0, ge=0, description="証拠金（資金）")


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
