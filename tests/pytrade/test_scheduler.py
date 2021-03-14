import pytest

from pytrade.builder import MarketStreamBuilder
from pytrade.portfolio import VirtualAccount


def test_get_seconds_or_days():
    """86400の倍数か、もしくは86400未満しか受け付けないこと"""
    from pytrade.schedulers import get_seconds_or_days

    assert get_seconds_or_days(0) == (0, 0)
    assert get_seconds_or_days(1) == (1, 0)
    assert get_seconds_or_days(60 * 60 * 24 - 1) == (86399, 0)
    assert get_seconds_or_days(60 * 60 * 24) == (0, 1)
    with pytest.raises(Exception):
        assert get_seconds_or_days(60 * 60 * 24 + 1)


def test_get_scheduler():
    from pytrade.schedulers import (
        CryptoWatchScheduler,
        RealtimeScheduler,
        TestScheduler,
    )

    expected = {
        "production": "realtime",
        "realtest": "realtime",
        "backtest": "backtest",
        "test": "test",
    }

    def must_be_1(mode):
        schedule_mode = MarketStreamBuilder.get_schedule_mode(mode=mode)
        if mode in expected:
            assert schedule_mode == expected[mode]
        else:
            assert schedule_mode is None

    must_be_1("production")
    must_be_1("realtest")
    must_be_1("backtest")
    must_be_1("test")
    must_be_1("asdfasdf")

    class_expected = {
        "production": RealtimeScheduler,
        "realtest": RealtimeScheduler,
        "backtest": CryptoWatchScheduler,
        "test": TestScheduler,
    }

    def must_be_2(mode):
        va = VirtualAccount()
        scheduler, schedule_mode = MarketStreamBuilder.get_scheduler(
            virtual_account=va, mode=mode
        )
        if mode in expected:
            assert schedule_mode == expected[mode]
            assert scheduler
            isinstance(scheduler, class_expected[mode])
        else:
            assert schedule_mode is None
            assert scheduler is None

    must_be_2("production")
    must_be_2("realtest")
    must_be_2("backtest")
    must_be_2("test")
    must_be_2("asdfasdf")
