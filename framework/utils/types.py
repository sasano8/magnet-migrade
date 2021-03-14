import datetime
from abc import ABC

import pytz
from pydantic import datetime_parse

tz_tokyo = pytz.timezone("Asia/Tokyo")
min_date_aware = tz_tokyo.localize(
    datetime.datetime(1901, 12, 15)
)  # 古すぎる日付は適切に扱うことが非常に難しため、問題が生じない日付のみ許容する。
min_date_naive = datetime.datetime(
    1901, 12, 15
)  # 古すぎる日付は適切に扱うことが非常に難しため、問題が生じない日付のみ許容する。


class DateTimeAware(datetime.datetime):
    def __new__(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = 0,
        minute: int = 0,
        second: int = 0,
        microsecond: int = 0,
        tzinfo=None,
        fold: int = 0,
    ):
        dic = locals()
        dic.pop("cls")

        if not tzinfo:
            tzinfo = datetime.timezone.utc
            dt = datetime.datetime(**dic)
            dt = pytz.utc.localize(dt)
        elif isinstance(tzinfo, pytz.tzinfo.BaseTzInfo):
            dic.pop("tzinfo")
            dt = tzinfo.localize(datetime.datetime(**dic))
        elif isinstance(tzinfo, datetime.tzinfo):
            dic.pop("tzinfo")
            dt = tzinfo.localize(datetime.datetime(**dic))

        return dt

    @classmethod
    def now(cls, tz=None):
        # tz is Noneならローカルタイムゾーンを設定する
        raise NotImplementedError()

    @classmethod
    def from_datetime(cls, dt: datetime.datetime):
        if dt.tzinfo is not None:
            return dt
        else:
            return cls(
                dt.year,
                dt.month,
                dt.day,
                dt.hour,
                dt.minute,
                dt.second,
                dt.microsecond,
                dt.tzinfo,
            )

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        v = datetime_parse.parse_datetime(v)
        v = cls.from_datetime(v)

        # if v.tzinfo is None:
        #     raise ValueError("timezone required.")

        if v < min_date_aware:
            raise ValueError("Can not be used dates before 1901/12/15")

        return v
