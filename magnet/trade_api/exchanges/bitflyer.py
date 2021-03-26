import datetime
import hashlib
import hmac
import json
from decimal import Decimal
from enum import Enum
from typing import List, Literal
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, parse_obj_as

from framework import DateTimeAware
from libs import create_params, decorators

from .. import enums


class Market(BaseModel):
    product_code: str
    market_type: str

    class Config:
        schema_extra = {"example": {"product_code": "BTC_JPY", "market_type": "Spot"}}


class BoardDetail(BaseModel):
    price: float
    size: float


class Board(BaseModel):
    mid_price: float
    bids: List[BoardDetail]
    asks: List[BoardDetail]

    class Config:
        schema_extra = {
            "example": {
                "mid_price": 1232.1,
                "bids": [{"price": 1156513.0, "size": 0.1}],
                "asks": [{"price": 1156513.0, "size": 0.1}],
            }
        }


class Ticker(BaseModel):
    product_code: str
    state: str
    timestamp: DateTimeAware
    tick_id: int
    best_bid: Decimal
    best_ask: Decimal
    best_bid_size: Decimal
    best_ask_size: Decimal
    total_bid_depth: Decimal
    total_ask_depth: Decimal
    market_bid_size: Decimal
    market_ask_size: Decimal
    ltp: Decimal
    volume: Decimal
    volume_by_product: Decimal


#
# class ProductCode(Enum):
#     pass


class TimeInForce(Enum):
    """
    Good 'Til Canceled - 注文が約定するかキャンセルされるまで有効であるという注文執行数量条件です。
    Immediate or Cancel - 指定した価格かそれよりも有利な価格で即時に一部あるいは全部を約定させ、約定しなかった注文数量をキャンセルさせる注文執行数量条件です。
    Fill or Kill - 発注の全数量が即座に約定しない場合当該注文をキャンセルする注文執行数量条件です。
    """

    gtc = "GTC"
    ioc = "IOC"
    fok = "FOK"


class BitflyerPublicAPI:
    name = enums.Exchange.BITFLYER
    # product_code = ProductCode

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    async def request_public(self, method: str, path: str, body: dict):
        url = "https://api.bitflyer.com" + path
        headers = {"Content-Type": "application/json"}

        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers, params=body)
            elif method == "POST":
                response = await client.post(
                    url, headers=headers, data=json.dumps(body)
                )
            else:
                raise Exception(f"Unkwon http method: {method}")

        try:
            response.raise_for_status()
        except httpx._exceptions.HTTPError as err:
            raise Exception(
                "[{}][{}]:{}".format(
                    response.status_code, response.reason_phrase, response.text
                )
            )

        return response

    async def request_private(self, method: str, path: str, body: dict):
        if method == "GET":
            body = urlencode(body)
            if body:
                path = path + "?" + body

        url = "https://api.bitflyer.com" + path
        timestamp = str(int(datetime.datetime.today().timestamp() * 1000))

        signature = self.create_sign(
            method=method, timestamp=timestamp, path=path, body=body
        )

        headers = {
            "ACCESS-KEY": self.api_key,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": signature,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            if method == "GET":
                response = await client.get(url, headers=headers)
            elif method == "POST":
                data = json.dumps(body)
                response = await client.post(url, headers=headers, data=data)
            else:
                raise Exception(f"Unkwon http method: {method}")

        try:
            # 200番台でなければ例外を発生させる
            response.raise_for_status()
        except httpx._exceptions.HTTPError as err:
            raise Exception(
                "[{}][{}]:{}".format(
                    response.status_code, response.reason_phrase, response.text
                )
            )

        return response

    def create_sign(self, method: str, timestamp: str, path: str, body: dict):
        if method == "GET":
            body = ""
        else:
            body = json.dumps(body)
        text = timestamp + method + path + body
        signature = hmac.new(
            bytearray(self.api_secret.encode("utf-8")),
            text.encode("utf-8"),
            hashlib.sha256,
        )
        digest = signature.hexdigest()
        return digest

    @decorators.MapJson
    async def get_markets(self) -> List[Market]:
        """マーケットの一覧を取得する。"""
        res = await self.request_private(method="GET", path="/v1/markets", body={})
        return res.text

    @decorators.MapJson
    async def get_board(self, product_code: str = "BTC_JPY") -> Board:
        """板情報を取得する。"""
        res = await self.request_private(
            method="GET",
            path="/v1/board",
            body=create_params(product_code=product_code),
        )
        return res.text

    # @decorators.MapJson
    async def get_ticker(self, product_code: str = "BTC_JPY") -> Ticker:
        """通貨の概要を取得する。"""
        res = await self.request_private(
            method="GET",
            path="/v1/ticker",
            body=create_params(product_code=product_code),
        )
        dic = json.loads(res.text)
        return parse_obj_as(Ticker, dic)

    async def get_executions(
        self,
        product_code: str = "BTC_JPY",
        count: int = 100,
        before: int = None,
        after: int = None,
    ):
        """約定履歴を取得する。"""
        res = await self.request_private(
            method="GET",
            path="/v1/executions",
            body=create_params(product_code=product_code),
        )
        return json.loads(res.text)

    @decorators.Decode
    async def get_boradstate(self, product_code: str = "BTC_JPY"):
        """約定履歴を取得する。"""
        res = await self.request_private(
            method="GET",
            path="/v1/getboardstate",
            body=create_params(product_code=product_code),
        )
        return res.text

    async def get_health(self, product_code: str = "BTC_JPY"):
        """
        取引所の状態を取得する。
        """
        res = await self.request_private(
            method="GET",
            path="/v1/gethealth",
            body=create_params(product_code=product_code),
        )
        return json.loads(res.text)

    async def get_chats(self, from_date):
        """チャットの発言一覧を取得します。"""
        res = await self.request_private(
            method="GET", path="/v1/getchats", body=create_params(from_date=from_date)
        )
        return json.loads(res.text)


class BitflyerPrivateAPI(BitflyerPublicAPI):
    async def get_permissions(self):
        """API キーの権限を取得する。"""
        res = await self.request_private(
            method="GET", path="/v1/me/getpermissions", body=dict()
        )
        return json.loads(res.text)

    async def get_balance(self):
        """資産残高を取得する。"""
        res = await self.request_private(
            method="GET", path="/v1/me/getbalance", body=dict()
        )
        return json.loads(res.text)

    async def get_collateral(self):
        """証拠金の状態を取得する。"""
        res = await self.request_private(
            method="GET", path="/v1/me/getcollateral", body=dict()
        )
        return json.loads(res.text)

    async def get_collateralaccounts(self):
        """通貨別の証拠金数量を取得する。"""
        res = await self.request_private(
            method="GET", path="/v1/me/getcollateralaccounts", body=dict()
        )
        return json.loads(res.text)

    async def get_address(self):
        """仮想通貨を bitFlyer アカウントに預入るためのアドレスを取得します。"""
        res = await self.request_private(
            method="GET", path="/v1/me/getaddresses", body=dict()
        )
        return json.loads(res.text)

    async def get_coinins(
        self, count: int = 100, before: int = None, after: int = None
    ):
        """仮想通貨預入履歴を取得する。"""
        res = await self.request_private(
            method="GET",
            path="/v1/me/getcoinins",
            body=create_params(count=count, before=before, after=after),
        )
        return json.loads(res.text)

    async def get_bankaccounts(self):
        res = await self.request_private(
            method="GET", path="/v1/me/getbankaccounts", body=dict()
        )
        return json.loads(res.text)

    async def get_deposits(
        self, count: int = 100, before: int = None, after: int = None
    ):
        res = await self.request_private(
            method="GET",
            path="/v1/me/getdeposits",
            body=create_params(count=count, before=before, after=after),
        )
        return json.loads(res.text)

    async def post_withdraw(
        self,
        bank_account_id: int,
        amount: float,
        currency_code: str = "JPY",
        code: str = None,
    ):
        """出金します。"""
        res = await self.request_private(
            method="POST",
            path="/v1/me/withdraw",
            body=create_params(
                bank_account_id=bank_account_id,
                amount=amount,
                currency_code=currency_code,
                code=code,
            ),
        )
        return json.loads(res.text)

    async def post_withdrawals(
        self, count: int = 100, before: int = None, after: int = None
    ):
        """出金履歴を取得する。"""
        res = await self.request_private(
            method="POST",
            path="/v1/me/getwithdrawals",
            body=create_params(count=count, before=before, after=after),
        )
        return json.loads(res.text)

    async def post_sendchildorder(
        self,
        product_code: str,
        child_order_type: Literal["LIMIT", "MARKET"],
        side: Literal["BUY", "SELL"],
        size: float,
        price: float = None,
        minute_to_expire: int = 43200,
        time_in_force: Literal["GTC", "IOC", "FOK"] = "GTC",
    ):
        """新規注文を出す。"""
        body = create_params(
            product_code=product_code,
            child_order_type=child_order_type,
            side=side,
            size=size,
            price=price,
            minute_to_expire=minute_to_expire,
            time_in_force=time_in_force,
        )

        res = await self.request_private(
            method="POST", path="/v1/me/sendchildorder", body=body
        )
        return json.loads(res.text)

    async def post_cancelchildorder(
        self,
        product_code: str,
        child_order_id: int = None,
        chile_order_acceptance_id=None,
    ):
        """注文をキャンセルする。"""
        body = create_params(
            product_code=product_code,
            child_order_id=child_order_id,
            chile_order_acceptance_id=chile_order_acceptance_id,
        )

        res = await self.request_private(
            method="POST", path="/v1/me/cancelchildorder", body=body
        )
        return json.loads(res.text)

    async def post_sendparentorder(
        self,
        order_method: Literal["SIMPLE", "IFD", "OCO", "IFDOCO"] = "SIMPLE",
        minute_to_expire: int = 43200,
        time_in_force: Literal["GTC", "IOC", "FOK"] = "GTC",
        parameters: List = [],
    ):
        """
        単純な指値注文 (LIMIT), 成り行き注文 (MARKET) 以外の、ロジックを含んだ注文を発注することができます。 このような注文は、親注文 (parent order) として扱われます。 特殊注文を利用することで、マーケットの状況に応じて注文を出したり、複数の注文を関連付けたりすることが可能です。
        """
        body = create_params(
            order_method=order_method,
            minute_to_expire=minute_to_expire,
            time_in_force=time_in_force,
            parameters=parameters,
        )

        res = await self.request_private(
            method="POST", path="/v1/me/sendparentorder", body=body
        )
        return json.loads(res.text)

    async def post_cancelparentorder(
        self,
        product_code: str,
        parent_order_id: int = None,
        parent_order_acceptance_id=None,
    ) -> Literal[""]:
        """親注文をキャンセルする。キャンセルはべき等性で応答が返り、何度実行してもOKが返る"""
        body = create_params(
            product_code=product_code,
            parent_order_id=parent_order_id,
            parent_order_acceptance_id=parent_order_acceptance_id,
        )

        res = await self.request_private(
            method="POST", path="/v1/me/cancelparentorder", body=body
        )
        return res.text  # 空テキストでjson.loads失敗が失敗するため、単に空テキストを返す

    async def post_cancelchildorder(self):
        raise NotImplementedError()

    async def post_cancelallchildorders(
        self,
        product_code: str,
    ):
        """すべての注文をキャンセルする。"""
        body = create_params(
            product_code=product_code,
        )

        res = await self.request_private(
            method="POST", path="/v1/me/cancelallchildorders", body=body
        )
        return json.loads(res.text)

    async def get_childorders(
        self,
        product_code: str,
        count: int = 100,
        before: int = None,
        after: int = None,
        chiled_order_state: Literal[
            "ACTIVE", "COMPLETED", "CANCELED", "EXPIRED", "REJECTED"
        ] = None,
        child_order_id: int = None,
        child_order_acceptance_id: int = None,
        parent_order_id: int = None,
    ):
        """注文の一覧を取得する。"""
        body = create_params(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
            chiled_order_state=chiled_order_state,
            child_order_id=child_order_id,
            child_order_acceptance_id=child_order_acceptance_id,
            parent_order_id=parent_order_id,
        )

        res = await self.request_private(
            method="GET", path="/v1/me/getchildorders", body=body
        )
        return json.loads(res.text)

    async def get_parentorders(
        self,
        product_code: str,
        count: int = 100,
        before: int = None,
        after: int = None,
        parent_order_state: Literal[
            "ACTIVE", "COMPLETED", "CANCELED", "EXPIRED", "REJECTED"
        ] = None,
    ):
        """親注文の一覧を取得する。"""
        body = create_params(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
            parent_order_state=parent_order_state,
        )

        res = await self.request_private(
            method="GET", path="/v1/me/getparentorders", body=body
        )
        return json.loads(res.text)

    async def get_parentorder(
        self, parent_order_id: int = None, parent_order_acceptance_id: str = None
    ):
        """親注文の詳細を取得する。"""
        body = create_params(
            parent_order_id=parent_order_id,
            parent_order_acceptance_id=parent_order_acceptance_id,
        )

        res = await self.request_private(
            method="GET", path="/v1/me/getparentorder", body=body
        )
        return json.loads(res.text)

    async def get_executions(
        self,
        product_code: str,
        count: int = 100,
        before: int = None,
        after: int = None,
        child_order_id: int = None,
        child_order_acceptance_id: int = None,
    ):
        """約定の一覧を取得する。"""
        body = create_params(
            product_code=product_code,
            count=count,
            before=before,
            after=after,
            child_order_id=child_order_id,
            child_order_acceptance_id=child_order_acceptance_id,
        )

        res = await self.request_private(
            method="GET", path="/v1/me/getexecutions", body=body
        )
        return json.loads(res.text)

    async def get_balancehistory(
        self,
        currency_code: str = "JPY",
        count: int = 100,
        before: int = None,
        after: int = None,
    ):
        """約定の一覧を取得する。"""
        body = create_params(
            currency_code=currency_code,
            count=count,
            before=before,
            after=after,
        )

        res = await self.request_private(
            method="GET", path="/v1/me/getbalancehistory", body=body
        )
        return json.loads(res.text)

    async def get_positions(
        self,
        product_code: str = "FX_BTC_JPY",
    ):
        """約定の一覧を取得する。"""
        body = create_params(
            product_code=product_code,
        )

        res = await self.request_private(
            method="GET", path="/v1/me/getpositions", body=body
        )
        return json.loads(res.text)

    async def get_collateralhistory(
        self, count: int = 100, before: int = None, after: int = None
    ):
        """証拠金の変動履歴を取得する。"""
        body = create_params(count=count, before=before, after=after)

        res = await self.request_private(
            method="GET", path="/v1/me/getcollateralhistory", body=body
        )
        return json.loads(res.text)

    async def get_tradingcommission(self, product_code: str):
        """取引手数料を取得する。"""
        body = create_params(product_code=product_code)

        res = await self.request_private(
            method="GET", path=f"/v1/me/gettradingcommission", body=body
        )
        return json.loads(res.text)


class BitflyerAPI(BitflyerPrivateAPI):
    pass
