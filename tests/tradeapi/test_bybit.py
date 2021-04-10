import asyncio
import os
from typing import cast

import ccxt.async_support as ccxt
from ccxt.async_support.bybit import bybit

# from magnet.config import APICredentialBinance
from pydantic import BaseSettings


class APICredentialBybit(BaseSettings):
    API_BYBIT_TEST_API_KEY: str
    API_BYBIT_TEST_API_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def API_BYBIT_API_KEY(self):
        return self.API_BYBIT_TEST_API_KEY

    @property
    def API_BYBIT_API_SECRET(self):
        return self.API_BYBIT_TEST_API_SECRET


credential = APICredentialBybit()

# https://github.com/ccxt/ccxt
exchange_id = "bybit"
exchange_class = getattr(ccxt, exchange_id)


def create_api() -> bybit:
    return exchange_class(
        {
            "apiKey": credential.API_BYBIT_API_KEY,
            "secret": credential.API_BYBIT_API_SECRET,
            "timeout": 30000,
            "enableRateLimit": True,
        }
    )


def ccxt_context(func):
    import functools

    # @functools.wraps(func)
    async def main():
        api: bybit = create_api()
        try:
            api.urls["api"] = api.urls["test"]
            await func(api)  # type: ignore
        except:
            raise
        finally:
            await api.close()

    def wrapped():
        asyncio.run(main())

    wrapped.__name__ = func.__name__
    wrapped.__module__ = func.__module__

    return wrapped


@ccxt_context
async def test_get_ticker(api: bybit):
    symbol = "BTC/USDT"
    ticker = await api.fetch_ticker(symbol=symbol)
    assert ticker["high"]


@ccxt_context
async def test_get_symbols(api: bybit):
    result = await api.v2PublicGetSymbols()
    assert result["result"]


@ccxt_context
async def test_set_leverage(api: bybit):
    result = await api.v2PrivatePostPositionLeverageSave(
        params={"symbol": "BTCUSDT", "leverage": 1}
    )
    assert result


@ccxt_context
async def main(api: bybit):
    import pprint

    # pprint.pprint(api.api)
    # https://note.com/kanawoinvestment/n/ne287ff725fd9

    markets = await api.load_markets()
    # print(markets)  printするとバグる、、、
    pairs = [x for x in api.symbols if "BTC" in x]
    symbol = "BTC/USDT"

    symbol = "BTC/USDT"
    order_type = "limit"
    side = "buy"
    amount = 1
    price = 50000

    # クロスマージン取引
    # 口座残高の全てを証拠金としてロックし、更に最大レバレッジをかける恐ろしいモード。レバレッジは、数量で調整する

    # 分離マージン取引
    # 注文分の証拠金のみをロックする。レバレッジを指定可能。

    symbol_new = symbol.replace("/", "")

    # USDTシンボルはこちら
    # https://help.bybit.com/hc/en-us/articles/360039260574-What-is-a-reduce-only-order-
    # https://help.bybit.com/hc/en-us/articles/360039260534-What-is-a-close-on-trigger-Order-
    if True:
        order = await api.private_linear_post_order_create(
            {
                "side": "Buy",
                "symbol": symbol_new,
                "order_type": "Market",  # Limit
                "qty": 1,  # 1BitCoin
                # "price": 1 # 1USD
                "take_profit": 1,  # 利確価格　1USD
                "stop_loss": 1,  # 損切価格　1USD
                "time_in_force": "GoodTillCancel",
                "reduce_only": False,  # オープンポジションがない場合、にリデュースのみの注​​文は拒否される。要は、クローズ注文として扱う場合に利用する。
                "close_on_trigger": False,  # システムが他のアクティブな注文を自動的にキャンセルして証拠金を解放
                # "order_link_id	": ""  # どの注文に関連するのか、カスタマイズでリンクしていい
            }
        )
        print(order)
