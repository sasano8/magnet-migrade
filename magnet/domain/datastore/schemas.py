import datetime
from decimal import Decimal
from typing import Iterable, List, Literal, Optional

from framework import DateTimeAware, Linq

from ...commons import BaseModel


class Pairs(BaseModel):
    id: Optional[int]
    provider: Literal["cryptowatch"]
    symbol: str


class CryptoBase(BaseModel):
    id: Optional[int]
    provider: Literal["cryptowatch"]
    market: Literal["bitflyer"]
    product: Literal["btcjpy"]
    periods: int


class Ohlc(CryptoBase):
    # id: Optional[int]
    # provider: Literal["cryptowatch"]
    # market: Literal["bitflyer"]
    # product: Literal["btcjpy"]
    # periods: int
    close_time: datetime.date
    start_time: datetime.date
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    quote_volume: float

    t_sma_5: float = None
    t_sma_10: float = None
    t_sma_15: float = None
    t_sma_20: float = None
    t_sma_25: float = None
    t_sma_30: float = None
    t_sma_200: float = None

    t_cross: int = None

    class Config:
        orm_mode = True

    @classmethod
    def compute_technical(cls, ohlc_arr: Iterable["Ohlc"]) -> "List[Ohlc]":
        import pandas as pd

        ohlc_arr = list(ohlc_arr)
        sr = Linq(ohlc_arr).map(lambda x: x.close_price).to_series()

        sma_5 = sr.rolling(5, min_periods=1).mean()  # 一週間　仮想通貨の場合は？？
        sma_10 = sr.rolling(10, min_periods=1).mean()
        sma_15 = sr.rolling(15, min_periods=1).mean()
        sma_20 = sr.rolling(20, min_periods=1).mean()
        sma_25 = sr.rolling(25, min_periods=1).mean()
        sma_30 = sr.rolling(30, min_periods=1).mean()
        sma_200 = sr.rolling(200, min_periods=1).mean()  # 取引所の年間営業日が200日程度

        for index, item in enumerate(ohlc_arr):
            item.t_sma_5 = sma_5[index]
            item.t_sma_10 = sma_10[index]
            item.t_sma_15 = sma_15[index]
            item.t_sma_20 = sma_20[index]
            item.t_sma_25 = sma_25[index]
            item.t_sma_30 = sma_30[index]
            item.t_sma_200 = sma_200[index]

            # ゴールデンクロス・デッドクロス検知
            if item.t_sma_5 > item.t_sma_25:
                item.t_cross = 1
            elif item.t_sma_5 < item.t_sma_25:
                item.t_cross = -1
            else:
                item.t_cross = 0

        previous_cross = 0

        for item in ohlc_arr:
            if previous_cross == item.t_cross:
                previous_cross = item.t_cross
                item.t_cross = 0

            else:
                previous_cross = item.t_cross

        return ohlc_arr


class CryptoTradeResult(CryptoBase):
    size: Decimal
    ask_or_bid: Literal[1, -1] = None
    entry_date: DateTimeAware
    entry_close_date: datetime.date = None
    entry_side: Literal["bid", "ask"]
    entry_price: Decimal
    entry_commission: Decimal
    entry_reason: str
    settle_date: DateTimeAware
    settle_close_date: datetime.date = None
    settle_side: Literal["bid", "ask"]
    settle_price: Decimal
    settle_commission: Decimal
    settle_reason: str
    job_name: str
    job_version: str
    is_back_test: bool = False
    close_date_interval: int = None
    diff_profit: Decimal = None
    diff_profit_rate: Decimal = None
    fact_profit: Decimal = None

    @property
    def _compute_ask_or_bid(self):
        if self.entry_side == "ask":
            return 1
        elif self.entry_side == "bid":
            return -1
        else:
            raise Exception()

    # @prop("profit_loss")
    @property
    def _compute_diff_profit(self):
        ask_or_bid = self._compute_ask_or_bid
        entry = self.entry_price
        settle = self.settle_price
        result = ask_or_bid * (settle - entry)
        return result  #  + self.entry_commission + self.settle_commission

    @property
    def _compute_diff_profit_rate(self):
        settle = self.entry_price + self.diff_profit
        try:
            result = settle / self.entry_price
        except:
            result = Decimal("1")
        return result

    @property
    def _compute_fact_profit(self):
        return self._compute_diff_profit * self.size

    @property
    def _compute_entry_close_date(self):
        return self.entry_date.date() + datetime.timedelta(days=1)

    @property
    def _compute_settle_close_date(self):
        return self.settle_date.date() + datetime.timedelta(days=1)

    @property
    def _compute_close_date_interval(self):
        return (self._compute_settle_close_date - self._compute_entry_close_date).days

    def dict(self, **kwargs):
        from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP

        self.ask_or_bid = self._compute_ask_or_bid
        self.entry_close_date = self._compute_entry_close_date
        self.settle_close_date = self._compute_settle_close_date
        self.close_date_interval = self._compute_close_date_interval
        self.diff_profit = self._compute_diff_profit
        self.diff_profit_rate = self._compute_diff_profit_rate.quantize(
            Decimal("0.0001"), rounding=ROUND_HALF_UP
        )
        self.fact_profit = self._compute_fact_profit.quantize(
            Decimal("0"), rounding=ROUND_HALF_UP
        )
        dic = super().dict(**kwargs)
        return dic


class Detail(BaseModel):
    url: Optional[str]
    url_cache: Optional[str]
    title: Optional[str]
    summary: Optional[str]

    class Config:
        extra = "allow"


class CommonSchema(BaseModel):
    # Config = ORM
    class Config:
        orm_mode = True

    # pipeline: str
    # crawler_name: str
    # keyword: str
    # option_keywords: List[str] = []
    # deps: int = 0
    referer: Optional[str]
    url: Optional[str]
    url_cache: Optional[str]
    title: Optional[str]
    summary: Optional[str]
    detail: Detail = Detail()

    def copy_summary(self):
        dic = self.dict(exclude={"detail"})
        obj = self.__class__.construct(**dic)
        return obj

    def sync_summary_from_detail(self):
        self.url = self.detail.url
        self.url_cache = self.detail.url_cache
        self.title = self.detail.title
        self.summary = self.detail.summary
