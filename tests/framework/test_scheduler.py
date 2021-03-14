import asyncio
from datetime import datetime

import pytest

from framework import DateTimeAware
from framework.scheduler import Scheduler


def test_by_datetimes():
    async def main():
        source = [DateTimeAware(2010, 1, x) for x in range(1, 32)]
        scheduler = Scheduler(source)
        return [x async for x in scheduler]

    results = asyncio.run(main())

    assert len(results) == 31
    assert results[0].day == 1
    assert results[1].day == 2
    assert results[29].day == 30
    assert results[30].day == 31
    with pytest.raises(IndexError):
        assert results[31].day == 32


def test_by_seconds():
    async def main():
        results = []

        async def nest():
            scheduler = Scheduler(second=1)
            async for x in scheduler:
                results.append(x)

        try:
            await asyncio.wait_for(nest(), timeout=1.1)
        except asyncio.TimeoutError:
            pass

        return results

    result = asyncio.run(main())
    assert len(result) == 1
    assert isinstance(result[0], datetime)
