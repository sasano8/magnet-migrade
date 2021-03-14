import datetime
from asyncio import sleep
from enum import Enum
from typing import Iterable

from framework import DateTimeAware


class WeekDay(int, Enum):
    Mon = 0
    Tue = 1
    Wed = 2
    Thu = 3
    Fri = 4
    Sat = 5
    Sun = 6


class SchedulerType(Enum):
    DATETIMES = 0
    SECOND = 1
    DAY = 2


class Scheduler:
    def __init__(
        self,
        source: Iterable[DateTimeAware] = None,
        second: float = None,
        hour: float = None,
        day: int = None,
        month: int = None,
        year: int = None,
        weeks: Iterable[WeekDay] = None,
    ) -> None:
        if source is not None:
            if (
                second is None
                and hour is None
                and day is None
                and month is None
                and year is None
                and weeks is None
            ):
                self.type = SchedulerType.DATETIMES
                self.source = list(source)
        else:
            if second is not None:
                if (
                    hour is None
                    and day is None
                    and month is None
                    and year is None
                    and weeks is None
                ):
                    self.type = SchedulerType.SECOND
                    self.second = second
                else:
                    raise Exception()
            else:
                if day and weeks:
                    raise NotImplementedError()
                else:
                    self.type = SchedulerType.DAY
                    self.day = day

    def __aiter__(self):
        if self.type == SchedulerType.DATETIMES:
            return self.iter_source()
        elif self.type == SchedulerType.SECOND:
            return self.iter_secound()
        else:
            raise NotImplementedError()

    async def iter_source(self):
        for d in self.source:
            await sleep(0)
            yield d

    async def iter_second(self):
        interval = self.second
        while True:
            await sleep(interval)
            yield DateTimeAware.utcnow()

    async def iter_days(self):
        # TODO: 真面目にやるなら調整機能が必要
        interval = self.day * (60 * 60 * 24)
        # datetime.timedelta(days=1) これで1日プラスされる　あとは時間を消す
        # utcならこれでいいが、ローカル時間の指定時間をどうするかが難しい
        # コンストラクタにタイムゾーンを指定させる
        while True:
            await sleep(interval)
            yield DateTimeAware.utcnow()
