import datetime
import hashlib
import hmac
import json
from typing import Literal, Optional
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel

from libs import decorators

from .. import enums


def remove_none_value_from_dic(**kwargs):
    removed = {k: v for k, v in kwargs.items() if v is not None}
    return removed


class Ticker(BaseModel):
    last: float
    high: float
    low: float
    vwap: float
    volume: float
    bid: float  # 買気配
    ask: float  # 売気配


class ZaifPlaceHolder(BaseModel):
    success: int
    error: Optional[str]
    return_: Optional[str]

    class Config:
        fields = {"from_": "from", "return_": "return"}
        schema_extra = {
            "example": {"success": 0, "error": "invalid currency_pair parameter"}
        }
        allow_population_by_field_name = True


from pydantic import BaseModel


class TradeResponse(BaseModel):
    received: float
    remains: float
    order_id: int  # 注文が全て成立した場合は0、もしくは、板に残った注文ID
    funds: dict  # 残高は後で照会すればよい

    class Config:
        schema_extra = {
            "example": {
                "received": 12.7972899,
                "remains": 0,
                "order_id": 0,
                "funds": {
                    "jpy": 112637.6587618,
                    "btc": 0,
                    "xem": 3745.2,
                    "mona": 0,
                    "ZAIF": 1016.1602,
                },
            }
        }


class TradeResponse(ZaifPlaceHolder):
    return_: TradeResponse


class ZaifPublicAPI:
    name = enums.Exchange.ZAIF
    # currency_pairs = enums.CurrencyPair

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    @staticmethod
    def _exclude_none_from_params(params: dict):
        return {k: v for k, v in params.items() if v is not None}

    async def request_public(self, url: str, params: dict = {}):
        encoded_params = urlencode(params)
        signature = hmac.new(
            bytearray(self.api_secret.encode("utf-8")), digestmod=hashlib.sha512
        )
        signature.update(encoded_params.encode("utf-8"))

        headers = dict(key=self.api_key, sign=signature.hexdigest())

        # response = httpx.post(url, headers=headers, data=encoded_params)
        # if response.status_code != 200:
        #     raise Exception("return status is {}".format(response.status_code))

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=encoded_params)

        return response

    async def request(self, url: str, params: dict = {}):
        params = self._exclude_none_from_params(params)
        encoded_params = urlencode(params)
        signature = hmac.new(
            bytearray(self.api_secret.encode("utf-8")), digestmod=hashlib.sha512
        )
        signature.update(encoded_params.encode("utf-8"))

        headers = dict(key=self.api_key, sign=signature.hexdigest())

        # response = httpx.post(url, headers=headers, data=encoded_params)
        # if response.status_code != 200:
        #     raise Exception("return status is {}".format(response.status_code))

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=encoded_params)

        return response

    # https://zaif-api-document.readthedocs.io/ja/latest/PublicAPI.html

    @decorators.Decode
    async def get_currencies(self, currency: str = "all"):
        url = f"https://api.zaif.jp/api/1/currency/{currency}"
        params = {}
        res = await self.request_public(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_currency_pairs(self, currency_pair: enums.zaif_currency_pair = "all"):
        url = f"https://api.zaif.jp/api/1/currency_pairs/{currency_pair}"
        params = {}
        res = await self.request_public(url=url, params=params)
        return res.text

    # async def get_currency_pairs_enum_string(self):
    #     arr = await self.get_currency_pairs()
    #     arr = list(map(lambda x: x["name"].lower(), arr))
    #     print(arr)
    #
    #     arr = await self.get_currency_pairs()
    #     arr = list(map(lambda x: x["currency_pair"].lower(), arr))
    #     print(arr)

    # get_tickerを使ったほうがよい
    @decorators.Decode
    async def get_last_price(self, currency_pair: enums.zaif_currency_pair):
        url = f"https://api.zaif.jp/api/1/last_price/{currency_pair}"
        params = {}
        res = await self.request_public(url=url, params=params)
        return res.text

    @decorators.MapJson
    async def get_ticker(self, currency_pair: enums.zaif_currency_pair) -> Ticker:
        url = f"https://api.zaif.jp/api/1/ticker/{currency_pair}"
        params = {}
        res = await self.request_public(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_trades(self, currency_pair: enums.zaif_currency_pair):
        """
        全ユーザの取引履歴を取得します。
        取得できる取引履歴は最新のものから最大150件となります。
        """
        url = f"https://api.zaif.jp/api/1/trades/{currency_pair}"
        params = {}
        res = await self.request_public(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_depth(self, currency_pair: enums.zaif_currency_pair):
        """
        板情報を取得します。
        売り情報は価格の昇順、買い情報は価格の降順でソートされた状態で返却されます。
        情報数は最大150件となります。
        """
        url = f"https://api.zaif.jp/api/1/depth/{currency_pair}"
        params = {}
        res = await self.request_public(url=url, params=params)
        return res.text


class ZaifTradingAPI(ZaifPublicAPI):
    # https://zaif-api-document.readthedocs.io/ja/latest/TradingAPI.html
    @decorators.Decode
    async def get_info(self):
        """
        現在の残高（余力および残高・トークン）、APIキーの権限、過去のトレード数、アクティブな注文数、サーバーのタイムスタンプを取得します。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(method="get_info", nonce=datetime.datetime.utcnow().timestamp())
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_info2(self):
        """
        get_infoの軽量版。過去のトレードを除く。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(method="get_info2", nonce=datetime.datetime.utcnow().timestamp())
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_id_info(self):
        """
        ユーザーIDやメールアドレスといった個人情報を取得します。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="get_id_info", nonce=datetime.datetime.utcnow().timestamp()
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_trade_history(
        self,
        from_: int = 0,
        count: int = 100,
        from_id: int = 0,
        end_id: int = None,  # float("inf") infinityを表す
        order: str = "DESC",
        since: int = 0,  # unix_timestamp
        end: int = None,  # unix_timestamp
        currency_pair: enums.zaif_currency_pair = None,
        is_token: bool = False,
    ):
        """
        ユーザー自身の取引履歴を取得します。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="trade_history",
            nonce=datetime.datetime.utcnow().timestamp(),
            count=count,
            from_id=from_id,
            end_id=end_id,
            order=order,
            since=since,
            end=end,
            currency_pair=currency_pair,
            is_token=is_token,
        )
        params["from"] = from_
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_active_orders(
        self,
        currency_pair: enums.zaif_currency_pair = None,
        is_token: bool = False,  # カウンターパーティトークンかどうか
        is_token_both: bool = False,  # 全てのアクティブなオーダー情報を取得 | currency_pairやis_tokenに従ったオーダー情報を取得
    ):
        """
        現在有効な注文一覧を取得します（未約定注文一覧）。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="active_orders",
            nonce=datetime.datetime.utcnow().timestamp(),
            currency_pair=currency_pair,
            is_token=is_token,
            is_token_both=is_token_both,
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def post_trade(
        self,
        currency_pair: enums.zaif_currency_pair,
        action: Literal["bid", "ask"],  # bid 買 ask 売
        price: float,
        amount: float,
        limit: float = None,
        comment: str = None,  # コメントを付与可能
    ):
        """
        取引注文を行います。
        """
        url = f"https://api.zaif.jp/tapi"
        params = remove_none_value_from_dic(
            method="trade",
            nonce=datetime.datetime.utcnow().timestamp(),
            currency_pair=currency_pair,
            action=action,
            price=price,
            amount=amount,
            limit=limit,
            comment=comment,
        )
        res = await self.request(url=url, params=params)
        # '{"success": 0, "error": "invalid currency_pair parameter"}'
        return res.text

    @decorators.Decode
    async def post_cancel_order(
        self,
        order_id: int,
        currency_pair: enums.zaif_currency_pair = None,
        is_token: bool = False,
    ):
        """
        注文の取消しを行います。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="cancel_order",
            nonce=datetime.datetime.utcnow().timestamp(),
            order_id=order_id,
            currency_pair=currency_pair,
            is_token=is_token,
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def post_withdraw(
        self,
        currency: str,
        address: str,
        amount: float,
        message: str = None,
        opt_fee: float = None,
    ):
        """
        資金の引き出しリクエストを送信します。 2015年12月15日より、Zaif内の振替を除くリクエストには一旦トランザクションIDは空で返されるようになりました。
        通常１～２分でトランザクションが発生しますので、後ほどwithdraw_historyメソッドを利用して確認してください。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="withdraw",
            nonce=datetime.datetime.utcnow().timestamp(),
            currency=currency,
            address=address,
            amount=amount,
            message=message,
            opt_fee=opt_fee,
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_deposit_history(
        self,
        currency: str = None,
        from_: int = 0,
        count: int = 1000,
        from_id: int = 0,
        end_id: int = None,
        order: str = "DESC",
        since: int = 0,
        end: int = None,
    ):
        """
        入金履歴を取得します。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="deposit_history",
            nonce=datetime.datetime.utcnow().timestamp(),
            currency=currency,
            count=count,
            from_id=from_id,
            end_id=end_id,
            order=order,
            since=since,
            end=end,
        )
        params["from"] = from_
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_withdraw_history(
        self,
        currency,
        from_: int = 0,
        count: int = 1000,
        from_id: int = 0,
        end_id: int = None,
        order: str = "DESC",
        since: int = 0,
        end: int = None,
    ):
        """
        get_infoの軽量版。過去のトレードを除く。
        """
        url = f"https://api.zaif.jp/tapi"
        params = dict(
            method="deposit_history",
            nonce=datetime.datetime.utcnow().timestamp(),
            currency=currency,
            count=count,
            from_id=from_id,
            end_id=end_id,
            order=order,
            since=since,
            end=end,
        )
        params["from"] = from_
        res = await self.request(url=url, params=params)
        return res.text


class ZaifMarginTradingAPI(ZaifTradingAPI):
    # https://zaif-api-document.readthedocs.io/ja/latest/MarginTradingAPI.html

    @decorators.Decode
    async def get_positions(
        self,
        group_id: int = None,
        from_: int = 0,
        count: int = 1000,
        from_id: int = 0,
        end_id: int = None,
        order: str = "DESC",
        since: int = 0,
        end: int = None,
        currency_pair: enums.zaif_currency_pair = None,
    ):
        """
        信用取引のユーザー自身の取引履歴を取得します。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="get_positions",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="futures",
            group_id=group_id,
            count=count,
            from_id=from_id,
            end_id=end_id,
            order=order,
            since=since,
            end=end,
            currency_pair=currency_pair,
        )
        params["from"] = from_
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_position_history(self, leverage_id: int, group_id: int = None):
        """
        信用取引のユーザー自身の取引履歴を取得します。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="position_history",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="futures",
            leverage_id=leverage_id,
            group_id=group_id,
        )
        res = await self.request(url=url, params=params)
        return res.text

    async def get_active_positions(
        self, group_id: int = None, currency_pair: enums.zaif_currency_pair = None
    ):
        """
        信用取引の現在有効な注文一覧を取得します（未約定注文一覧）。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="active_positions",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="futures",
            group_id=group_id,
            currency_pair=currency_pair,
        )
        res = await self.request(url=url, params=params)
        return json.loads(res.text)

    async def get_create_position(self, group_id: int, leverage_id: int):
        """AirFXのユーザー自身の取引履歴の明細を取得します。"""
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="create_position",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="futures",
            group_id=group_id,
            leverage_id=leverage_id,
        )
        res = await self.request(url=url, params=params)
        return json.loads(res.text)

    @decorators.Decode
    async def post_create_position(
        self,
        currency_pair: enums.zaif_currency_pair,
        action: Literal["bid", "ask"],  # bid 買 ask 売
        amount: float,
        price: float,
        leverage: float,
        group_id: int,  # 任意にグルーピングするためのid。必須
        limit: float = None,
        stop: float = None,
    ):
        """
        信用取引の注文を行います。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="create_position",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="futures",
            currency_pair=currency_pair,
            action=action,
            amount=amount,
            price=price,
            leverage=leverage,
            group_id=group_id,
            limit=limit,
            stop=stop,
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def post_change_position(
        self,
        currency_pair: enums.zaif_currency_pair,
        leverage_id: float,
        price: float,
        group_id: int = None,
        limit: float = None,
        stop: float = None,
    ):
        """
        信用取引の注文の変更を行います。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="change_position",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="margin",
            currency_pair=currency_pair,
            leverage_id=leverage_id,
            price=price,
            group_id=group_id,
            limit=limit,
            stop=stop,
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def post_cancel_position(
        self,
        leverage_id: float,
        group_id: int = None,
    ):
        """
        信用取引の注文の取消しを行います。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="get___",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="margin",
            leverage_id=leverage_id,
            group_id=group_id,
        )
        res = await self.request(url=url, params=params)
        return res.text

    @decorators.Decode
    async def get_(
        self,
        group_id: int = None,
        from_: int = 0,
        count: int = 1000,
        from_id: int = 0,
        end_id: int = None,
        order: str = "DESC",
        since: int = 0,
        end: int = None,
        currency_pair: enums.zaif_currency_pair = None,
    ):
        """
        信用取引のユーザー自身の取引履歴を取得します。
        """
        url = f"https://api.zaif.jp/tlapi"
        params = dict(
            method="get___",
            nonce=datetime.datetime.utcnow().timestamp(),
            type="futures",
        )
        res = await self.request(url=url, params=params)
        return res.text


class ZaifAirFXAPI(ZaifMarginTradingAPI):
    pass


class ZaifWebSocket_API(ZaifAirFXAPI):
    pass


class ZaifOAuthAPI(ZaifWebSocket_API):
    pass


class ZaifPaymentAPI(ZaifOAuthAPI):
    pass


# @decorators.Instantiate(api_key=Env.api_credentials["zaif"].api_key.get_secret_value(), api_secret=Env.api_credentials["zaif"].api_secret.get_secret_value())
class ZaifAPI(ZaifPaymentAPI):
    pass
