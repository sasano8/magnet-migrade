import decimal
import logging
from typing import Any, Dict, Literal, Optional, Union

from pydantic import Field, validator

from ...commons import BaseModel

logger = logging.getLogger(__name__)


class TradeOrderCreate(BaseModel):
    class Config:
        orm_mode = True

    broker: str = "test"
    description: str = ""
    provider: str
    market: str
    product: str
    bid_or_ask: Literal["ask", "bid"]
    order_type: Literal["market", "limit"]
    kwargs: Dict[str, Any] = {}


class TradeOrderCreated(TradeOrderCreate):
    """本システムに登録され、idが発行されている状態を表す"""

    id: int


class TradeOrderAccepted(TradeOrderCreated):
    """外部APIより、注文が受理されている状態を表す"""

    acceptance_id: str = Field("", description="APIから発行された受け入れIDを格納してもよい。")
    external_data: dict = Field({}, description="fetch時にAPIから返される任意の注文情報を格納してもよい")
    is_contracted: bool = Field(False, const=False)
    is_cancelled: bool = False


class TradeOrderPositioned(TradeOrderAccepted):
    """注文の一部だけでなく、全て約定している状態を表す"""

    is_cancelled: bool = Field(const=False)
    is_contracted: bool = Field(const=True)
