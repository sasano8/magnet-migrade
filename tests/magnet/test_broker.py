import asyncio

from magnet.domain.order import Broker


def test_bitfflyer():
    # return  # テストする時にのみ外してください

    async def main():
        broker = Broker("bitflyer")
        # markets = await broker.get_markets()
        # print(markets)
        result = await broker.run_test(timeout=100)

    asyncio.run(main())
