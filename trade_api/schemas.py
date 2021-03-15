import datetime
from typing import Optional

from pydantic import BaseModel

from framework import DateTimeAware


class TickerInfo(BaseModel):
    product_common: str
    exchange: str
    product: str
    close_time: datetime.date
    current_time: DateTimeAware
    last: float
    high: float
    low: float
    volume: float
    quote_volume: Optional[float] = None
    vwap: Optional[float] = None
    # volume_by_product: float
    # bid: float = None
    # ask: float = None
