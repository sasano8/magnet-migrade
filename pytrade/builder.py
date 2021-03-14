from typing import List, Literal, Tuple

from pydantic import BaseModel

from pp.protocols import PCancelToken
from pp.types import CancelToken

from .algorithms import Algorithms, Decisions
from .portfolio import Account, TradePosition, VirtualAccount
from .schedulers import (
    CryptoWatchScheduler,
    RealtimeScheduler,
    Scheduler,
    TestScheduler,
)
from .stream import Broker, Dealer, MarketStream

__all__ = ["get_cancel_token", "main", "PCancelableToken"]


def get_cancel_token() -> CancelToken:
    """"""
    return CancelToken()


brokers = {}
datastores = {}
# schedulers = {}


def register_broker(name: str, broker):
    if name in brokers:
        raise KeyError(f"duplicate {name}")
    brokers[name] = broker


def register_datastore(name: str, datastore):
    if name in datastores:
        raise KeyError(f"duplicate {name}")
    datastores[name] = datastore


# class Job(BaseModel):
#     version: int = 0
#     name: str = 0
#     description: str = ""
#     mode: Literal["production", "backtest", "test"]
#     market: str
#     product: str
#     periods: Literal[1, 86400]
#     # provider: Literal["cryptowatch"]
#     broker: Literal["bitflyer", "zaif"] = "bitflyer"
#     backtest_scheduler: Literal["cryptowatch"] = "cryptowatch"


async def run(
    job,
    cancel_token: PCancelToken,
    mode: Literal["production", "backtest", "test"] = "backtest",
):
    stream = build_market_stream(job, mode=mode)
    cancel_token = {}
    await stream(cancel_token)
    print("")
    for x in stream.decision_log:
        print(x)


class MarketStreamBuilder:
    __analyzers__ = {
        "always_buy": Algorithms.always_buy,
        "always_close": Algorithms.always_close,
        "random": Algorithms.random,
        "t_cross": Algorithms.t_cross,
    }
    __limitloss__ = {
        "limit": Algorithms.limit,
        "loss": Algorithms.loss,
    }
    __decisions__ = {"default": Decisions.default}
    __scheduler__ = {
        "realtime": RealtimeScheduler,
        "test": TestScheduler,
        "backtest": CryptoWatchScheduler,
    }
    __broker__ = {
        "bitflyer": None,
        "zaif": None,
    }

    def __init__(self, virtual_account: VirtualAccount):
        self.virtual_account = virtual_account

    @staticmethod
    def get_schedule_mode(
        mode: Literal["production", "realtest", "backtest", "test"]
    ) -> str:
        if mode == "production" or mode == "realtest":
            deal_mode = "realtime"
        else:
            deal_mode = mode

        if deal_mode not in {"realtime", "backtest", "test"}:
            deal_mode = None

        return deal_mode

    @classmethod
    def get_scheduler(
        cls,
        virtual_account: VirtualAccount,
        mode: Literal["production", "realtest", "backtest", "test"],
        market: str = "",
    ) -> Tuple[Scheduler, Literal["realtime", "backtest", "test"]]:
        schedule_mode = cls.get_schedule_mode(mode=mode)
        SchedulerClass = cls.__scheduler__.get(schedule_mode, None)
        if not SchedulerClass:
            return (None, None)  # type: ignore
        scheduler = SchedulerClass(
            market=market,
            product=virtual_account.product,
            periods=virtual_account.periods,
        )
        return (scheduler, schedule_mode)  # type: ignore

    @classmethod
    def get_broker(
        cls,
        virtual_account: VirtualAccount,
        mode: Literal["production", "realtest", "backtest", "test"],
    ):
        pass
        # get_topic
        #

    def get_stream(
        self, mode: Literal["production", "realtest", "backtest", "test"]
    ) -> Tuple[MarketStream, CancelToken]:
        """MarketStreamを生成する

        Args:
            mode:
              - production: 実際に取引を行う
              - realtest: 実際に取引を行わなないが、リアルタイムな情報でシミュレーションを行う
              - backtest: 過去データ(providerのデータ)を用いて、取引を検証する
              - test: 実際に取引を行わず、簡単な動作確認のみを行う

        Returns:
            Tuple[MarketStream, CancelToken]: [description]
        """
        virtual_account = self.virtual_account
        analyzers = self.__analyzers__
        limitloss = self.__limitloss__
        decisions = self.__decisions__

        dealer = Dealer(
            virtual_account=virtual_account,
            analyzer_repository=analyzers,
            limitloss_repository=limitloss,
            dicision_repository=decisions,
        )
        dealer.is_valid()
        scheduler, scheduler_mode = self.get_scheduler(
            virtual_account=virtual_account, mode=mode
        )
        # broker = self.get_broker(virtual_account=virtual_account, mode=mode)
        broker = Broker(virtual_account=virtual_account, position=None, budget=0)
        allocated_margin = 0

        # ポジションを復元

        # ルールを復元
        # limit_lossはそのポジションに依存する。

        stream = MarketStream(dealer=dealer, scheduler=scheduler, broker=broker)
        return (stream, CancelToken())
