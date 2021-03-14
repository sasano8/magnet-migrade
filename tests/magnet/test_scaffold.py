import datetime

import pytest
import pytz

from magnet.domain.scaffold import models, schemas

from .conftest import engine, override_get_db

tz_utc = pytz.timezone("UTC")
tz_tokyo = pytz.timezone("Asia/Tokyo")


def test_platform():
    """sqliteやpostgresなどデータベースによって挙動が変わると思う"""
    assert engine.url.drivername == "postgresql"
    assert engine.driver == "psycopg2"


def test_date_naive():
    """
    awareとnativeな日付の挙動を確認する。これは、仕様確認としてのテストである。
    とりあえず分かったことは、utc環境でawareとnativeな時間を比較しても、同じ時間を指していても一致しない。
    """
    # naiveな日付の場合、タイムゾーンは保持されない
    for db in override_get_db():
        # rep = crud.Dummy(db)
        rep = models.Dummy.as_rep()
        obj = rep.create(
            db,
            **schemas.Dummy(
                name="date_naive: datetime naive",
                date_naive=datetime.datetime(2020, 1, 1),
            ).dict()
        )

        db.flush()
        assert obj.date_naive.tzinfo is None
        db.commit()
        assert obj.date_naive.tzinfo is None
        assert obj.date_naive == datetime.datetime(2020, 1, 1)

    # utc awareな日付の場合、タイムゾーンは破棄される ⇛　破棄されていない
    for db in override_get_db():
        target_dt = tz_utc.localize(datetime.datetime(2020, 1, 1))
        # rep = crud.Dummy(db)
        rep = models.Dummy.as_rep()
        obj = rep.create(
            db,
            **schemas.Dummy(
                name="date_naive: datetime aware utc", date_naive=target_dt
            ).dict()
        )

        assert obj.date_naive.tzinfo
        db.flush()
        assert obj.date_naive.tzinfo
        db.commit()
        assert obj.date_naive.tzinfo is None
        assert obj.date_naive != target_dt  # タイムゾーンが破棄されていたが、いつの間にか保持されるようになっていた、、、
        assert obj.date_naive == datetime.datetime(2020, 1, 1)  # タイムゾーン有無で比較が異なる

    # jst awareな日付の場合、タイムゾーンは破棄されるが、utc時間に変換される（日本時間は、utc時間より9時間進んでいる。）
    for db in override_get_db():
        target_dt = tz_tokyo.localize(datetime.datetime(2020, 1, 1))
        # 日本時間2020/1/1はutc時間2019/12/31 15:00
        assert target_dt == tz_utc.localize(
            datetime.datetime(2020, 1, 1)
        ) - datetime.timedelta(hours=9)
        # utc時間2020/1/1は日本時間2020/1/1 9:00
        assert target_dt + datetime.timedelta(hours=9) == tz_utc.localize(
            datetime.datetime(2020, 1, 1)
        )

        # rep = crud.Dummy(db)
        rep = models.Dummy.as_rep()
        obj = rep.create(
            db,
            **schemas.Dummy(
                name="date_naive: datetime aware jst", date_naive=target_dt
            ).dict()
        )
        assert obj.date_naive.tzinfo
        db.flush()
        assert obj.date_naive.tzinfo
        db.commit()
        assert obj.date_naive.tzinfo is None
        assert obj.date_naive.timestamp() == target_dt.timestamp()
        assert obj.date_naive != target_dt  # 比較できないらしい

        # 日本時間2020/1/1 すなわち utc時間2019/12/31 15:00に対応するnaiveな日付が登録されている
        assert obj.date_naive == datetime.datetime(2020, 1, 1) - datetime.timedelta(
            hours=9
        )


def test_date_aware():
    """tzが設定されるのはデータベースコミット時"""
    # naiveな日付を登録した場合、utc(offset=0)として扱われる
    for db in override_get_db():
        # rep = crud.Dummy(db)
        rep = models.Dummy.as_rep()
        obj = rep.create(
            db,
            **schemas.Dummy(
                name="date_aware: datetime naive",
                date_aware=datetime.datetime(2020, 1, 1),
            ).dict()
        )

        assert obj.date_aware.tzinfo is None
        db.flush()
        assert obj.date_aware.tzinfo is None
        db.commit()
        assert obj.date_aware.tzinfo
        assert obj.date_aware != datetime.datetime(2020, 1, 1)  # awareとnaiveは比較できない
        assert obj.date_aware == tz_utc.localize(
            datetime.datetime(2020, 1, 1)
        )  # aware同士のため比較可能

    # utc awareな日付の場合
    for db in override_get_db():
        target_dt = tz_utc.localize(datetime.datetime(2020, 1, 1))
        # rep = crud.Dummy(db)
        rep = models.Dummy.as_rep()
        obj = rep.create(
            db,
            **schemas.Dummy(
                name="date_aware: datetime aware utc", date_aware=target_dt
            ).dict()
        )
        db.flush()
        assert obj.date_aware.tzinfo
        db.commit()
        assert obj.date_aware.tzinfo  # offset0のタイムゾーンを保持
        assert obj.date_aware != datetime.datetime(2020, 1, 1)  # awareとnaiveは比較できない
        assert obj.date_aware == target_dt  # タイムゾーンは維持されるため比較可能

    # jst awareな日付の場合
    for db in override_get_db():
        target_dt = tz_tokyo.localize(datetime.datetime(2020, 1, 1))
        # 日本時間2020/1/1はutc時間2019/12/31 15:00
        assert target_dt == tz_utc.localize(
            datetime.datetime(2020, 1, 1)
        ) - datetime.timedelta(hours=9)
        # utc時間2020/1/1は日本時間2020/1/1 9:00
        assert target_dt + datetime.timedelta(hours=9) == tz_utc.localize(
            datetime.datetime(2020, 1, 1)
        )

        # rep = crud.Dummy(db)
        rep = models.Dummy.as_rep()
        obj = rep.create(
            db,
            **schemas.Dummy(
                name="date_aware: datetime aware jst", date_aware=target_dt
            ).dict()
        )
        db.flush()
        assert obj.date_aware.tzinfo  # offset0のタイムゾーンを保持
        db.commit()
        assert obj.date_aware.tzinfo
        assert obj.date_aware != datetime.datetime(2020, 1, 1)  # awareとnaiveは比較できない
        assert obj.date_aware == target_dt  # タイムゾーンは維持されるため比較可能

        # 日本時間2020/1/1はutc時間2019/12/31 15:00
        assert target_dt == tz_utc.localize(
            datetime.datetime(2020, 1, 1)
        ) - datetime.timedelta(hours=9)
        assert target_dt != datetime.datetime(2020, 1, 1) - datetime.timedelta(
            hours=9
        )  # awareとnaiveは比較できない
