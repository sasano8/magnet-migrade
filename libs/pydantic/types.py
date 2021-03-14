import datetime
from typing import Protocol, Type, Union

import pytz
from pydantic import datetime_parse

tz_tokyo = pytz.timezone("Asia/Tokyo")
min_date_aware = tz_tokyo.localize(
    datetime.datetime(1901, 12, 15)
)  # 古すぎる日付は適切に扱うことが非常に難しため、問題が生じない日付のみ許容する。
min_date_naive = datetime.datetime(
    1901, 12, 15
)  # 古すぎる日付は適切に扱うことが非常に難しため、問題が生じない日付のみ許容する。


class DateTimeNaive(datetime.datetime):
    """nativeなdatetimeオブジェクト用の型チェッカー。awareは許容されません。"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        v = datetime_parse.parse_datetime(v)
        if v.tzinfo:
            raise ValueError("timezone not allow.")

        if v < min_date_naive:
            raise ValueError("Can not be used dates before 1901/12/15")

        return v


class DateNaive(datetime.datetime):
    """nativeを許容するdatetimeオブジェクト用の型チェッカー。awareは許容されません。"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        v = datetime_parse.parse_datetime(v)
        if v.tzinfo:
            raise ValueError("timezone not allow.")
        v.replace(hour=0, minute=0, second=0, microsecond=0)

        if v < min_date_naive:
            raise ValueError("Can not be used dates before 1901/12/15")

        return v


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


class DateTime(DateTimeAware):
    """awareなdatetimeオブジェクト用の型チェッカー。現地時間を厳密に区別するため、タイムゾーンを保持したい場合に、使用します。"""


class DateTimeUtc(DateTimeAware):
    """awareなdatetimeオブジェクト用の型チェッカー。タイムゾーンは、utcに変更されます。"""

    @classmethod
    def validate(cls, v):
        v = super().validate(v)
        v = v.astimezone(datetime.timezone.utc)
        return v


class Date(DateTimeAware):
    """awareなdatetimeオブジェクト用の型チェッカー。datetimeを渡すと、時刻情報0のdatetime型(疑似date型)が作成されます。現地時間を厳密に区別するため、タイムゾーンを保持したい場合に、使用します。"""

    def __new__(
        cls,
        year: int,
        month: int,
        day: int,
        hour: int = ...,
        minute: int = ...,
        second: int = ...,
        microsecond: int = ...,
        tzinfo=...,
        fold: int = 0,
    ):
        self = super().__new__(
            cls, year, month, day, hour, minute, second, microsecond, tzinfo, fold=fold
        )
        self = self.replace(hour=0, minute=0, second=0, microsecond=0)
        return self

    @classmethod
    def validate(cls, v):
        v = super().validate(v)
        return v


class DateUtc(Date):
    """
    :type datetime.datetime:
    awareなdatetimeオブジェクト用の型チェッカー。datetimeを渡すと、時刻情報0のdatetime型(疑似date型)が作成されます。タイムゾーンは、utcに変更されます。
    """

    @classmethod
    def validate(cls, v):
        # replaceとastimezoneの実行順序は変えないこと。(テストしてないけどね！てへぺろ！)
        # サマータイムなどで影響が生じる可能性がある。
        v = super().validate(v)
        v = v.astimezone(
            datetime.timezone.utc
        )  # 1. 2020/1/1 9:10 11 123456 +9:00 2. 2020/1/1 +9:00(2019/12/31 15) 3. 2019/12/31になる　なぜ
        return v
