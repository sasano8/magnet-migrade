import datetime

import pytest
from pydantic import BaseModel

from framework import DateTimeAware


def test_datetime_aware():
    expected = datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc)

    assert DateTimeAware(2010, 1, 1) == expected
    assert DateTimeAware(2010, 1, 1) != datetime.datetime(2010, 1, 1)


def test_pydantic():
    class A(BaseModel):
        dt: DateTimeAware

    obj = A(dt=datetime.datetime(2010, 1, 1))
    assert obj.dt == datetime.datetime(2010, 1, 1, tzinfo=datetime.timezone.utc)


def test_any():
    assert datetime.datetime.utcnow().tzinfo is None
    assert DateTimeAware.utcnow().tzinfo

    assert datetime.datetime.now().tzinfo is None

    with pytest.raises(Exception):
        # 未実装
        DateTimeAware.now()


def test_aa():
    assert datetime.datetime.utcnow().strftime(
        "%Y%m%d_%H%M%S"
    ) == DateTimeAware.utcnow().strftime("%Y%m%d_%H%M%S")
