import enum
from decimal import ROUND_FLOOR, Decimal
from typing import List, Optional, Protocol, Union

from pydantic import BaseModel as BA
from pydantic import Field, validator

from framework import DateTimeAware
from pytrade import properties


class PositionStatus(int, enum.Enum):
    CANCELED = -2
    CANCELE_REQUESTED = -1
    READY = 0
    REQUESTED = 1
    CONTRACTED = 2


class AskBid(str, enum.Enum):
    ASK = "ask"
    BID = "bid"

    @staticmethod
    def invert(ask_or_bid: "AskBid"):
        if ask_or_bid.ASK:
            return AskBid.BID
        elif ask_or_bid.BID:
            return AskBid.ASK
        else:
            raise ValueError(ask_or_bid)


class BaseModel(BA):
    class Config:
        extra = "forbid"


class TradePosition(BaseModel, properties.TradePositionProperty):
    id: int
    # user_id: int
    # trade_account_id: int
    # trade_virtual_account_id: int
    entry_id: int = None
    is_backtest: bool = True
    provider: str
    market: str
    product: str
    periods: int
    status: PositionStatus = PositionStatus.READY
    ask_or_bid: AskBid
    order_at: DateTimeAware
    order_price: Decimal
    order_unit: Decimal
    contract_at: DateTimeAware = None
    contract_price: Decimal = None
    contract_unit: Decimal = None
    slippage_rate: Decimal = None
    limit_price: Decimal = None
    loss_price: Decimal = None
    profit_loss: Decimal = 0
    commission: Decimal = 0
    api_data: dict = {}
    reason: str = ""


class VirtualAccount(BaseModel):
    class Config:
        orm_mode = True

    name: str = ""
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
    id: int = None
    user_id: int = None
    trade_account_id: int = None
    version: int = 0
    description: str = ""
    position: TradePosition = None
    position_id: int = None


class Account(BaseModel):
    class Config:
        orm_mode = True

    # システム連携用　ライブラリでは使用しない
    id: Optional[Union[None, int]] = None
    user_id: int = None
    version: int = 0
    provider: str = ""
    market: str = ""

    # ライブラリの挙動に影響するフィールド
    name: str = ""
    description: str = ""  # 影響なし
    margin: Decimal = Field(0, ge=0, description="証拠金（資金）")
    accounts: List[VirtualAccount] = Field([], description="仮想口座一覧")

    @property
    def allocated_margin(self) -> Decimal:
        amount = Decimal("0")
        for account in self.accounts:
            amount += account.allocated_margin
        return amount

    @property
    def free_margin(self) -> Decimal:
        return self.margin - self.allocated_margin

    def reallocation(self):
        """仮想口座の証拠金割合に従って、証拠金の再割当てを行ったAccountインスタンスを返す"""
        accounts = []
        for account in self.accounts:
            margin = self.margin * account.allocation_rate
            margin = margin.quantize(Decimal("0"), rounding=ROUND_FLOOR)
            obj = account.copy(update={"allocated_margin": margin})
            accounts.append(obj)
        return self.copy(update={"accounts": accounts}, deep=True)

    @validator("accounts")
    def valid_no_conflict_id(cls, v):
        raise_if_conflict_account_id(v)
        return v

    @validator("accounts")
    def valid_over_allocated(cls, v: List[VirtualAccount]):
        """物理アカウントに紐づく仮想アカウントの合計割当率が100%を超えている場合に例外を発生させる"""
        all_rate = sum([account.allocation_rate for account in v])
        if all_rate > 1:
            raise OverAllocatedError(
                f"Can't allocation `allocation rate` over 100% -> {all_rate}"
            )
        return v


class Portfolio(BaseModel):
    class Config:
        orm_mode = True

    name: str = ""
    accounts: List[Account] = Field([], description="口座一覧")

    # システム連携用
    # user_id: int = None

    @property
    def margin(self) -> Decimal:
        amount = Decimal("0")
        for account in self.accounts:
            amount += account.margin
        return amount

    @property
    def allocated_margin(self) -> Decimal:
        amount = Decimal("0")
        for account in self.accounts:
            amount += account.allocated_margin
        return amount

    def _reallocation(self):
        accounts = [x.reallocation() for x in self.accounts]
        return self.copy(update={"accounts": accounts}, deep=True)

    def reallocation(self) -> "Portfolio":
        allocated = self._reallocation()
        self.raise_if_allocated_over_margin()
        return allocated

    def raise_if_allocated_over_margin(self):
        """物理口座の証拠金を超える仮想口座の証拠金が割り当てられていた時に例外を発生させる。
        reallocationせずに、仮想口座のallocated_marginを手動で設定した場合に、例外が発生しうる。
        """
        PortfolioAllocation(accounts=self.accounts)

    @validator("accounts")
    def valid_no_conflict_id(cls, v: List[Account]):
        raise_if_conflict_account_id(v)
        # 物理アカウントをまたがる仮想アカウント名も衝突を許可しない
        ids = set()
        for account in v:
            for vaccount in account.accounts:
                if vaccount.id in ids:
                    raise ConflictIdError(
                        f"{account.id}.{vaccount.id}: conflict virtual account id"
                    )
                ids.add(vaccount.id)
        return v


# reallocationからは事前制約があるため、基本的に例外が発生することはないが、一応検証しておく
# テストでは、allocated_marginをベタ打ちして、無理やり発生させる
class PortfolioAllocation(BaseModel):
    accounts: List[Account]

    @validator("accounts")
    def raise_if_megative_free_margin(cls, v: List[Account]):
        for account in v:
            if account.free_margin < 0:
                raise OverMarginError(
                    f"{account.id}: 不正な証拠金の割当 -> 超過={account.free_margin * -1} "
                )
        return v


class TradeError(ValueError):
    pass


class ConflictIdError(TradeError):
    pass


class OverAllocatedError(TradeError):
    pass


class OverMarginError(TradeError):
    pass


def raise_if_conflict_account_id(v: List[Account]):
    ids = set()
    for account in v:
        if account.id in ids:
            raise ConflictIdError(f"{account.id}: conflict account id")
        ids.add(account.id)
