import asyncio
import os
from typing import cast

import ccxt.async_support as ccxt
from ccxt.async_support.binance import binance

# from magnet.config import APICredentialBinance
from pydantic import BaseSettings


class APICredentialBinance(BaseSettings):
    API_BINANCE_API_KEY: str
    API_BINANCE_API_SECRET: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


credential = APICredentialBinance()


# https://github.com/ccxt/ccxt
exchange_id = "binance"
exchange_class = getattr(ccxt, exchange_id)


def create_api() -> binance:
    return exchange_class(
        {
            "apiKey": credential.API_BINANCE_API_KEY,
            "secret": credential.API_BINANCE_API_SECRET,
            "timeout": 30000,
            "enableRateLimit": True,
        }
    )


def ccxt_context(func):
    import functools

    @functools.wraps(func)
    async def wapped():
        api: binance = create_api()
        try:
            await func(api)
        except:
            raise
        finally:
            await api.close()

    return wapped


@ccxt_context
async def main(api):
    markets = await api.load_markets()
    # print(markets)  printするとバグる、、、
    pairs = [x for x in api.symbols if "BTC" in x]
    # print(pairs)
    symbol = "BTC/USDT"
    side = "buy"
    amount = 1
    quantity = 1  # amountとのニュアンスの違いが分からない
    price = 10000

    ticker = await api.fetch_ticker(symbol)  # get_ticker
    # https://github.com/ccxt/ccxt/issues/6345
    # https://github.com/ccxt/ccxt/wiki/Manual#api-method-naming-conventions  implicit rule

    if False:
        order = await api.create_order(
            symbol=symbol,
            type="market",  # limit or market
            side=side,
            amount=1,
            # price=
            params={"type": "margin", "test": False},
        )

    if False:
        delete_order = await api.sapiDeleteMarginOrder(
            {"orderId": 10, "symbol": symbol, "params": {"test": False}}
        )
        # {"code":-3003,"msg":"Margin account does not exist."}

    if True:
        symbol_new = symbol.replace("/", "")
        # 買いなら、売りに対する決済
        # 売りなら、買いに対する決済
        order = await api.private_post_order_oco(
            {
                "symbol": symbol_new,
                "side": side,
                "quantity": quantity,
                "price": 50000,
                "stopPrice": 60000,
                "stopLimitPrice": 60000,
                "stopLimitTimeInForce": "GTC",
            }
        )

    # ストップリミットオーダー
    # ストップ（トリガー）価格で実際に取引を行うリミット注文を発注
    # ストップとリミットを同じにすれば単なる成行のようにふるまう
    # トリガーに対して、少し下（買の場合）を指定するのが一般的？
    # めんどくさいからトリガーとリミットは一緒でよい

    # OCO
    # リミットとストップリミットの合わせ技　従来のリミットロス（利確・損切ライン）と捉える
    # 注文の仕方
    # Limit - Price - 利確価格
    # Stop-Limit - Stop - 損切り注文を発注する価格
    # Stop-Limit - Limit - 損切り価格

    # 注文プログラムの設計
    # 1. marketで注文
    # 2. OCOで利確損切り範囲を注文
    # 3. もしくは、2をキャンセルして任意のタイミングで成行決済
