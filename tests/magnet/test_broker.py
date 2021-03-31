import asyncio

from magnet.domain.trade.abc import TestBroker
from magnet.domain.trade.brokers import BitflyerBroker


def test_bitfflyer():
    return  # テストする時にのみ外してください

    async def main():
        broker = BitflyerBroker("key", "secret")
        test_broker = TestBroker(broker=broker)
        # markets = await broker.get_markets()
        # print(markets)
        result = await test_broker.run_test(timeout=100)

    asyncio.run(main())
