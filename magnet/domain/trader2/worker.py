import asyncio
from typing import Literal, Protocol, Type, runtime_checkable

from pydantic import BaseModel

from framework import DateTimeAware
from framework.scheduler import Scheduler
from pp.protocols import PCancelToken
from pp.types import CancelToken
from pytrade.stream import Algorithms, Broker, MarketStream, Position, make_decision

from .schemas import TradeAccount


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


class Job(BaseModel):
    version: int = 0
    name: str = 0
    description: str = ""
    mode: Literal["production", "backtest", "test"]
    market: str
    product: str
    periods: Literal[1, 86400]
    # provider: Literal["cryptowatch"]
    broker: Literal["bitflyer", "zaif"] = "bitflyer"
    backtest_scheduler: Literal["cryptowatch"] = "cryptowatch"


@runtime_checkable
class PSchedulerFactory(Protocol):
    @staticmethod
    def get_scheduler(
        market: str,
        product: str,
    ) -> Scheduler:
        pass


# def register_scheduler(scheduler_factory: Type[PSchedulerFactory]):
#     name = scheduler_factory.__name__
#     assert issubclass(scheduler_factory, PSchedulerFactory)
#     if name in schedulers:
#         raise KeyError(f"duplicate {name}")
#     schedulers[name] = scheduler_factory
#     return scheduler_factory


class CryptoWatchScheduler(PSchedulerFactory):
    @staticmethod
    def get_scheduler(
        market: str,
        product: str,
    ):
        from magnet.database import get_db
        from magnet.domain.datastore.models import CryptoOhlc

        for db in get_db():
            query = CryptoOhlc.Q_select_start_time(
                db,
                provider="cryptowatch",
                market=market,
                product=product,
                periods=60 * 60 * 24,
                order_by="asc",
            )
            scheduler = Scheduler(query)
        return scheduler


class TestScheduler(PSchedulerFactory):
    @staticmethod
    def get_scheduler(
        market: str,
        product: str,
    ):
        return Scheduler([DateTimeAware(2015, 1, x) for x in range(1, 32)])


class DailyScheduler(PSchedulerFactory):
    @staticmethod
    def get_scheduler(
        market: str,
        product: str,
    ):
        return Scheduler(day=1)


class SecondScheduler(PSchedulerFactory):
    @staticmethod
    def get_scheduler(
        market: str,
        product: str,
    ):
        return Scheduler(second=1)


async def run(job: TradeAccount, cancel_token: PCancelToken, mode: str):
    stream = build_market_stream(job, mode=mode)
    cancel_token = {}
    await stream(cancel_token)
    print("")
    for x in stream.decision_log:
        print(x)


def build_market_stream(
    job: TradeAccount, mode: Literal["production", "backtest", "test"] = "backtest"
):
    if len(job.accounts) != 1:
        raise NotImplementedError()

    for account in job.accounts:
        allocated_margin = account.allocated_margin
        if mode == "backtest":
            scheduler = CryptoWatchScheduler.get_scheduler(
                market=job.market, product=account.product
            )
        elif mode == "test":
            scheduler = TestScheduler.get_scheduler(
                market=job.market, product=account.product
            )
        elif mode == "production":
            if account.periods == 1:
                scheduler = SecondScheduler.get_scheduler(
                    job.market, product=account.product
                )
            elif account.periods == 60 * 60 * 24:
                scheduler = DailyScheduler.get_scheduler(
                    job.market, product=account.product
                )
            else:
                raise NotImplementedError()
        else:
            raise NotImplementedError()

    # ポジションを復元

    # ルールを復元
    # limit_lossはそのポジションに依存する。

    return MarketStream(
        scheduler=scheduler,
        broker=Broker(Position(), budget=allocated_margin),
        create_decisions=(Algorithms.decision_t_cross,),
        make_decision=make_decision,
    )
