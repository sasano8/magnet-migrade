from typing import Protocol, Tuple, runtime_checkable

from framework import DateTimeAware
from framework.scheduler import Scheduler


@runtime_checkable
class PSchedulerFactory(Protocol):
    @staticmethod
    def get_scheduler(market: str, product: str, periods: int) -> Scheduler:
        pass


# def register_scheduler(scheduler_factory: Type[PSchedulerFactory]):
#     name = scheduler_factory.__name__
#     assert issubclass(scheduler_factory, PSchedulerFactory)
#     if name in schedulers:
#         raise KeyError(f"duplicate {name}")
#     schedulers[name] = scheduler_factory
#     return scheduler_factory


def get_seconds_or_days(periods: int) -> Tuple[int, int]:
    if periods < (60 * 60 * 24):
        return (periods, 0)

    if not periods % (60 * 60 * 24) == 0:
        raise Exception()
    days = periods / (60 * 60 * 24)
    return (0, int(days))


class RealtimeScheduler(Scheduler):
    def __init__(self, market: str, product: str, periods: int):
        seconds, days = get_seconds_or_days(periods)
        if days:
            super().__init__(day=days)
        elif seconds:
            super().__init__(second=seconds)
        else:
            raise Exception()


class TestScheduler(Scheduler):
    """実際の時間ではなく、仮想的な時間を待機なしで流します"""

    def __init__(self, market: str, product: str, periods: int):
        seconds, days = get_seconds_or_days(periods)
        # TODO:　適当なのでもうちょっとまともに作る
        if days:
            schedule = [DateTimeAware(2020, 2, 1)]
        elif seconds:
            schedule = [DateTimeAware(2020, 2, 1, second=1)]
        else:
            raise Exception()
        super().__init__(schedule)


class CryptoWatchScheduler(Scheduler):
    """実際の時間ではなく、データベースに保存されているバックテストできる日付を取得し、待機なしで流します"""

    def __init__(self, market: str, product: str, periods: int):
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
        return super().__init__(query)
