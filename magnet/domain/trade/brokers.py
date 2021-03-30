from decimal import ROUND_HALF_UP, Decimal
from typing import Any, Dict, Literal, Union

from fastapi.encoders import jsonable_encoder

from trade_api import BitflyerAPI

from ...config import APICredentialBitflyer
from .abc import BrokerImpl
from .repository import BrokerRepository
from .schemas import OrderResult, PreOrder, TradeResult


@BrokerRepository.register
class BitflyerBroker(BrokerImpl):
    _name = "bitflyer"
    client: BitflyerAPI

    def __init__(self, api_key="", api_secret="") -> None:
        self.client = BitflyerAPI(
            api_key=api_key or APICredentialBitflyer().API_BITFLYER_API_KEY,
            api_secret=api_secret or APICredentialBitflyer().API_BITFLYER_API_SECRET,
        )

    async def get_markets(self):
        """取り扱っている商品などを取得する。主にデバッグ用"""
        return await self.client.get_markets()

    def convert_to_order(self, order: PreOrder):
        """リミットストップ付きの成行注文か、単なる成行注文を作成する"""
        product_code = order.product_code
        side = order.side
        size = order.size
        invert_side = "SELL" if side == "BUY" else "BUY"

        limit_price = order.limit_price
        stop_price = order.stop_price

        assert (limit_price is not None and stop_price is not None) or (
            limit_price is None and stop_price is None
        )

        if limit_price is not None and limit_price > 10000:
            # ビットコインなどは5円単位じゃないと発注できないので大きい値は四捨五入する
            limit_price = limit_price.quantize(0, rounding=ROUND_HALF_UP)
            stop_price = stop_price.quantize(0, rounding=ROUND_HALF_UP)

        if limit_price is None:
            # SIMPLEでMARKET・LIMITを注文できないので、しょうがないから利確目標価格を指値（成行と同等な挙動）にし、片方をキャンセルさせる
            # ２つ注文を入れるのでマージンが２倍必要になってしまう
            if side == "BUY":
                limit_price = (order.target_price * Decimal("1.05")).quantize(
                    0, rounding=ROUND_HALF_UP
                )
            else:
                limit_price = (order.target_price * Decimal("0.95")).quantize(
                    0, rounding=ROUND_HALF_UP
                )

            input = {
                "order_method": "OCO",  # ２つ注文を投げ、どちらかの約定のみ有効とする
                "minute_to_expire": 60 * 60 * 24 * 365,  # １年有効
                "time_in_force": "GTC",  # 失効数量条件 注文が約定するかキャンセルされるまで有効。激しく動いている時が苦手。
                "parameters": [
                    {
                        "product_code": product_code,
                        "condition_type": "LIMIT",
                        "side": side,
                        "size": size,
                        "price": limit_price,
                    },
                    # 約定することのないダミー注文
                    {
                        "product_code": product_code,
                        "condition_type": "TRAIL",
                        "side": side,  # 買の場合は、offset下落したら買うという文脈になる
                        "size": size,
                        "offset": 100000,
                    },
                ],
            }
        else:
            input = {
                "order_method": "IFD",  # 最初の注文が約定した後に自動的に 2つめの注文を行う
                "minute_to_expire": 60 * 60 * 24 * 365,  # １年有効
                "time_in_force": "GTC",  # 失効数量条件 注文が約定するかキャンセルされるまで有効。激しく動いている時が苦手。
                "parameters": [
                    {
                        "product_code": product_code,
                        "condition_type": "MARKET",  # 成行でエントリー
                        "side": side,
                        "size": size,
                    },
                    {
                        # 利確・損切（クローズストラテジー）
                        "product_code": product_code,
                        "condition_type": "STOP_LIMIT",
                        "side": invert_side,  # エントリーの逆を入力
                        "size": size,
                        "price": limit_price,  # エントリーの方向のリミット価格
                        "trigger_price": stop_price,  # エントリーに逆光したリミット価格　# STOP_LIMIT 利確もロスカットも指値で実施する
                        "offset": 0,  # TRAILの時に必須だが、STOP_LIMITでも必要っぽい（仕様書漏れ）。値動きに合わせてストップを自動更新する。0なら固定？
                    },
                ],
            }

        return jsonable_encoder(input)

    async def get_ticker(self, product_code):
        return await self.client.get_ticker(product_code)

    def localize_product_code(self, product_code: str) -> str:
        dic = {"btcjpy": "BTC_JPY", "btcfxjpy": "FX_BTC_JPY"}
        return dic[product_code]

    def localize_order(self, order: PreOrder) -> PreOrder:
        """ローカライズ処理"""
        dic_side = {1: "BUY", -1: "SELL"}

        product_code = self.localize_product_code(order.product_code)
        side = dic_side[order.side]

        order = PreOrder.construct(
            product_code=product_code,
            side=side,
            **order.dict(exclude={"product_code", "side"})
        )

        return order

    # def get_product_code_mapping(self) -> Dict[str, str]:
    #     return {"btcjpy": "BTC_JPY", "btcfxjpy": "FX_BTC_JPY"}

    async def order(self, order: PreOrder):
        converted_order = self.convert_to_order(order)
        accepted_data = await self.order_to_api(converted_order)
        return accepted_data

    async def order_test(self):
        """apiにテスト用の注文をリクエストする"""

        # product_code = "BTC_JPY"  # 現物の口座にないと取引できない？？
        product_code = "FX_BTC_JPY"  # 手数料が高く流動性が高いのテストに向かない
        ticker = await self.get_ticker(self.localize_product_code(product_code))
        latest_ticker_price = ticker.ltp
        # order = PreOrder(
        #     product_code=product_code,
        #     side="BUY",
        #     entry_price=latest_ticker_price,
        #     size=0.01,
        #     limit_rate=1.0001,
        #     stop_rate=0.9999,
        # )
        order = self.create_pre_order(
            budget=Decimal("100000"),
            product_code=product_code,  # 現物の口座にないと取引できない？？
            side=1,
            target_price=latest_ticker_price,
            limit_rate=1.0001,
            stop_rate=0.9999,
        )

        order = self.localize_preorder(order)
        converted_order = self.convert_to_order(order)
        return await self.order_to_api(converted_order)

    async def order_to_api(self, converted_order):
        product_code = converted_order["parameters"][0]["product_code"]
        accepted = await self.client.post_sendparentorder(**converted_order)
        accepted_data = {
            "product_code": product_code,
            "converted_order": converted_order,
            "accepted": accepted,
        }
        return accepted_data

    async def fetch_order_status(self, accepted_data) -> Union[Any, None]:
        """最新の注文状態を取得し、後続の処理で必要なデータを任意で返す。"""
        product_code = accepted_data["product_code"]
        parent_order_acceptance_id = accepted_data["accepted"][
            "parent_order_acceptance_id"
        ]

        order_data = await self.client.get_parentorder(
            parent_order_acceptance_id=parent_order_acceptance_id,
        )
        parent_order_id = order_data["parent_order_id"]

        # parent_idでフィルタできない
        parents = await self.client.get_parentorders(
            product_code=product_code, parent_order_state="ACTIVE"
        )

        parent = [x for x in parents if x["parent_order_id"] == parent_order_id]
        if len(parent):
            status = False
        else:
            # キャンセル・注文失効・約定の場合
            status = True

        status_data = {
            "parent_order_id": parent_order_id,
            "product_code": product_code,
            "is_completed": status,
            "accepted_data": accepted_data,
        }

        return status_data

    def is_completed(self, status_data) -> bool:
        return status_data["is_completed"]

    async def order_cancel(self, accepted_data):
        product_code = accepted_data["product_code"]
        parent_order_acceptance_id = accepted_data["accepted"][
            "parent_order_acceptance_id"
        ]
        accepted_cancel_data = await self.client.post_cancelparentorder(
            product_code=product_code,
            parent_order_acceptance_id=parent_order_acceptance_id,
        )
        return accepted_cancel_data

    async def finalize(self, status_data) -> TradeResult:
        product_code = status_data["product_code"]
        parent_order_id = status_data["parent_order_id"]
        children = await self.client.get_childorders(
            product_code=product_code, parent_order_id=parent_order_id
        )
        status_data["children"] = children
        result = self.get_finalized(status_data)
        return result

    async def order_close(self, finalized_data):
        return super().order_close(finalized_data)

    def get_finalized(self, status_data):
        # SAMPLE DATA
        # contracted = [{
        # 'id': 2453296368,
        # 'child_order_id': 'JFX20210315-162625-971434F',  # 注文の一部もしくは全部が約定した時に発行されるid
        # 'product_code': 'FX_BTC_JPY',
        # 'side': 'BUY',
        # 'child_order_type': 'MARKET',
        # 'price': 0.0,
        # 'average_price': 6489971.0,
        # 'size': 0.01,
        # 'child_order_state': 'COMPLETED',
        # 'expire_date': '2021-03-18T04:26:25',
        # 'child_order_date': '2021-03-15T16:26:25',
        # 'child_order_acceptance_id': 'JRF20210315-162625-040439',  #リクエストが受理された時に発行されるid
        # 'outstanding_size': 0.0,
        # 'cancel_size': 0.0,
        # 'executed_size': 0.01,
        # 'total_commission': 0.0
        # }]
        product_code = status_data["product_code"]
        is_fx = "FX" in product_code
        contracted = status_data["children"]
        buy = []
        sell = []

        for x in contracted:
            if x["side"] == "BUY":
                buy.append(x)
            elif x["side"] == "SELL":
                sell.append(x)
            else:
                raise Exception()

        def calculate(contracted, sdf: bool):
            if not contracted:
                return None

            total_size = Decimal("0")
            total_average = Decimal("0")
            total_commission = Decimal("0")

            for x in contracted:
                total_commission += Decimal(str(x["total_commission"]))
                size = Decimal(str(x["executed_size"]))
                total_size += size
                total_average += Decimal(str(x["average_price"])) * size

            average_price = total_average / total_size

            if sdf:
                # 現物とFXの価格乖離が激しいと、エントリー時にSFDというペナルティが生じる
                # 約定金額の0.25%(1% = 0.01)から〜2%かかる。現物価格取得したり計算が難しいので、ざっくり計算する（大体0.25%だが、多く見積もって0.5%とする）
                other_commision = (
                    average_price * total_size * Decimal("0.01") * Decimal("0.5")
                )
            else:
                other_commision = 0

            return OrderResult(
                average_price=average_price,
                executed_size=total_size,
                total_commission=total_commission,
                other_commission=other_commision,
            )

        result_buy = calculate(buy, is_fx)
        result_sell = calculate(sell, False)

        return TradeResult(
            product_code_localized=status_data["product_code"],
            buy=result_buy,
            sell=result_sell,
        )
