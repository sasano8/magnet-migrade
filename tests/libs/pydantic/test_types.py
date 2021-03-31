# type: ignore
import datetime

import pytest
import pytz
from pydantic import BaseModel

from libs.pydantic.types import (
    Date,
    DateNaive,
    DateTime,
    DateTimeNaive,
    DateTimeUtc,
    DateUtc,
)


class Model(BaseModel):
    date_time_naive: DateTimeNaive = None
    date_naive: DateNaive = None
    date_time: DateTime = None
    date_time_utc: DateTimeUtc = None
    date: Date = None
    date_utc: DateUtc = None


def test_naive_success_if_not_has_timezone():
    has_not_timezone = datetime.datetime.now()
    assert Model(date_time_naive=has_not_timezone)
    assert Model(date_naive=has_not_timezone)


def test_naive_raise_if_has_timezone():
    has_timezone = datetime.datetime.now(tz=datetime.timezone.utc)
    with pytest.raises(ValueError, match="timezone not allow"):
        Model(date_time_naive=has_timezone)
    with pytest.raises(ValueError, match="timezone not allow"):
        assert Model(date_naive=has_timezone)


def test_aware_success_if_has_timezone():
    has_timezone = datetime.datetime.now(tz=datetime.timezone.utc)
    assert Model(date_time=has_timezone)
    assert Model(date_utc=has_timezone)
    assert Model(date=has_timezone)
    assert Model(date_utc=has_timezone)

    has_timezone_iso = "2020-11-18T01:50:39.580616+09:00"
    assert Model(date_time=has_timezone_iso)
    assert Model(date_utc=has_timezone_iso)
    assert Model(date=has_timezone_iso)
    assert Model(date_utc=has_timezone_iso)


def test_aware_success_if_not_has_timezone():
    has_not_timezone = datetime.datetime.now()
    assert Model(date_time=has_not_timezone)
    assert Model(date_utc=has_not_timezone)
    assert Model(date=has_not_timezone)
    assert Model(date_utc=has_not_timezone)

    has_not_timezone_iso = "2020-11-17T15:47:37.141113"
    assert Model(date_time=has_not_timezone_iso)
    assert Model(date_utc=has_not_timezone_iso)
    assert Model(date=has_not_timezone_iso)
    assert Model(date_utc=has_not_timezone_iso)


def test_timezone():
    """
    datetimeとtimezoneの挙動やバグがあることを確認
    """

    # dst - daylignt saving time. サマータイムのこと。
    # jdt - Japan daylignt saving time

    # このやり方は19分ずれるので好ましくない
    tz = pytz.timezone("Asia/Tokyo")
    utc = pytz.timezone("utc")
    tokyo_ng = datetime.datetime(
        year=2020,
        month=1,
        day=1,
        hour=9,
        minute=10,
        second=11,
        microsecond=123456,
        tzinfo=tz,
    )
    tokyo_ok = tz.localize(
        datetime.datetime(
            year=2020, month=1, day=1, hour=9, minute=10, second=11, microsecond=123456
        )
    )

    tokyo_ng = tokyo_ng.astimezone(utc)
    tokyo_ok = tokyo_ok.astimezone(utc)
    assert (tokyo_ok - tokyo_ng) == datetime.timedelta(minutes=19)  # 19分の差が生じる

    # 本来1988/1/1を堺に切り替わるはずなのだが、unixtimeの最小値以下となるためかまともに働かない？
    # そのため、最古の日付は1901/12/15に制限した方が安全
    lmt = tz.localize(
        datetime.datetime(1901, 12, 15)
        - datetime.timedelta(hours=18, minutes=14, seconds=8, microseconds=1)
    )
    jst = tz.localize(
        datetime.datetime(1901, 12, 15)
        - datetime.timedelta(hours=18, minutes=14, seconds=8)
    )

    assert lmt.tzinfo.tzname != jst.tzinfo.tzname
    # assert lmt == jst

    # 実は日本にもサマータイムが存在した
    # 1948年5月2日　〜　1952年9月10日
    # 1949年（昭和24年）のみ4月）第1土曜日24時（= 日曜日0時）から9月第2土曜日25時（= 日曜日0時）までの間に夏時間
    # システム的には1948年5月2日１時〜 utc時間に１時間加えた時間をタイムゾーンとする
    jdt = tz.localize(
        datetime.datetime(1948, 5, 3) - datetime.timedelta(hours=23, microseconds=1)
    )
    assert jdt.tzname() == "JST"

    jdt = tz.localize(datetime.datetime(1948, 5, 3) - datetime.timedelta(hours=23))
    # print(jdt.tzinfo.tzname)  # <DstTzInfo 'Asia/Tokyo' JDT+10:00:00 DST>>
    assert jdt.tzname() == "JDT"

    jdt = tz.localize(
        datetime.datetime(1951, 5, 7) - datetime.timedelta(hours=23, microseconds=1)
    )
    assert jdt.tzname() == "JST"

    jdt = tz.localize(datetime.datetime(1951, 5, 7) - datetime.timedelta(hours=23))
    assert jdt.tzname() == "JDT"

    jdt = tz.localize(
        datetime.datetime(1951, 9, 9) - datetime.timedelta(microseconds=1)
    )
    assert jdt.tzname() == "JDT"

    jdt = tz.localize(datetime.datetime(1951, 9, 9))
    assert jdt.tzname() == "JST"

    # 1952年から廃止
    jdt = tz.localize(datetime.datetime(1952, 7, 10))
    assert jdt.tzname() == "JST"


def test_aware_datetime_value():
    # 同じ日付情報なら、DateTimeとDateTimeUTCは同じ値であることを確認
    utc = datetime.datetime(
        year=2020,
        month=1,
        day=1,
        hour=9,
        minute=10,
        second=11,
        microsecond=123456,
        tzinfo=datetime.timezone.utc,
    )
    assert utc == Model(date_time=utc).date_time
    assert utc == Model(date_time_utc=utc).date_time_utc

    # 同様に、ISOから確認
    utc_iso = "2020-01-01T09:10:11.123456+00:00"
    assert utc == Model(date_time=utc_iso).date_time
    assert utc == Model(date_time_utc=utc_iso).date_time_utc

    # タイムゾーンがUTCであること
    assert "UTC" == Model(date_time=utc_iso).date_time.tzname()
    assert "UTC" == Model(date_time_utc=utc_iso).date_time_utc.tzname()

    tz = pytz.timezone("Asia/Tokyo")
    tokyo = tz.localize(
        datetime.datetime(
            year=2020, month=1, day=1, hour=9, minute=10, second=11, microsecond=123456
        )
    )
    assert tokyo == Model(date_time=tokyo).date_time
    assert tokyo == Model(date_time_utc=tokyo).date_time_utc

    tokyo_iso = "2020-01-01T09:10:11.123456+09:00"
    assert tokyo == Model(date_time=tokyo_iso).date_time
    assert tokyo == Model(date_time_utc=tokyo_iso).date_time_utc
    assert (
        "2020-01-01T09:10:11.123456+09:00"
        == Model(date_time=tokyo_iso).date_time.isoformat()
    )
    assert (
        "2020-01-01T00:10:11.123456+00:00"
        == Model(date_time_utc=tokyo_iso).date_time_utc.isoformat()
    )

    assert "JST" == Model(date_time=tokyo).date_time.tzname()  # 地域を特定するタイムゾーンが取得可能
    assert "UTC" == Model(date_time_utc=tokyo).date_time_utc.tzname()

    assert (
        "UTC+09:00" == Model(date_time=tokyo_iso).date_time.tzname()
    )  # isoから復元した場合は、オフセットしか取得できない
    assert "UTC" == Model(date_time_utc=tokyo_iso).date_time_utc.tzname()

    assert Model(date_time=tokyo).date_time == Model(date_time=tokyo_iso).date_time
    assert (
        Model(date_time_utc=tokyo).date_time_utc
        == Model(date_time_utc=tokyo_iso).date_time_utc
    )


def test_aware_date_value():
    # 同じ日付情報なら、DateTimeとDateTimeUTCは同じ値であることを確認
    # かつ時刻情報が失われることを確認
    expected = datetime.datetime(
        year=2020, month=1, day=1, tzinfo=datetime.timezone.utc
    )
    utc = datetime.datetime(
        year=2020,
        month=1,
        day=1,
        hour=9,
        minute=10,
        second=11,
        microsecond=123456,
        tzinfo=datetime.timezone.utc,
    )
    assert expected == Model(date_utc=utc).date_utc
    assert expected == Model(date=utc).date

    # 同様に、ISOから確認
    utc_iso = "2020-01-01T09:10:11.123456+00:00"
    assert expected == Model(date_utc=utc_iso).date_utc
    assert expected == Model(date=utc_iso).date

    # タイムゾーンがUTCであること
    assert "UTC" == Model(date_utc=utc_iso).date_utc.tzname()
    assert "UTC" == Model(date=utc_iso).date.tzname()

    # Asia/Tokyoの2020/1/1 9:00~ の日付は UTC 2020/1/1と等しいこと
    expected = datetime.datetime(
        year=2020, month=1, day=1, tzinfo=datetime.timezone.utc
    )
    tz = pytz.timezone("Asia/Tokyo")
    tokyo = tz.localize(
        datetime.datetime(
            year=2020, month=1, day=1, hour=9, minute=10, second=11, microsecond=123456
        )
    )
    # 日本時間 2020/1/1 9:10 ⇛ UTC 2020/1/1 0:10 にすると2019/12/31 15:00 +0:00となり、2019/12/31となる
    assert expected == Model(date_utc=tokyo).date_utc
    assert (
        tz.localize(datetime.datetime(year=2020, month=1, day=1))
        == Model(date=tokyo).date
    )
