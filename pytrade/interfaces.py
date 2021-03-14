from decimal import Decimal
from typing import List, Protocol, Union

from pydantic import BaseModel, Field

from .portfolio import AskBid


class PTradePositionDeal(Protocol):
    ask_or_bid: AskBid
    limit_price: Union[Decimal, None] = None
    loss_price: Union[Decimal, None] = None


class BTradePositionDeal(BaseModel):
    ask_or_bid: AskBid
    limit_price: Union[Decimal, None] = None
    loss_price: Union[Decimal, None] = None


class BVirtualAccount(BaseModel):
    allocation_rate: Decimal = Field(0, ge=0, le=1, description="物理口座内の割合。")
    allocated_margin: Decimal = Field(
        0,
        ge=0,
        description="証拠金（資金）。reallocationを行った際に、rateと整合性が取れる。",
    )
    product: str = ""
    periods: int = 60 * 60 * 24
    analyzers: List[str] = []
    decision: str = "default"
    ask_limit_rate: Decimal = Field(0, ge=0)
    ask_loss_rate: Decimal = Field(0, ge=0)
    bid_limit_rate: Decimal = Field(0, ge=0)
    bid_loss_rate: Decimal = Field(0, ge=0)

    # system
    # id: int = None
    # user_id: int = None
    # trade_account_id: int = None
    # version: int = 0
    # description: str = ""
    # position: BTradePositionDeal = None
    position_id: int = None
