import random
from typing import Union

from .stream import BuyAndSellSignal, DealMessage, Topic


class Algorithms:
    async def empty(topic: Topic):
        """常に何も判断しません。テスト用アルゴリズムです。"""
        return None

    async def always_buy(topic: Topic):
        """常に買いの指示を送出します。これは、テスト用アルゴリズムです。"""
        return DealMessage(buy_and_sell=BuyAndSellSignal.BUY, reason="always_buy")

    async def always_close(topic: Topic):
        """ポジションを持っていれば常にクローズの指示を送出します。これは、テスト用アルゴリズムです。"""
        return DealMessage(buy_and_sell=BuyAndSellSignal.CLOSE, reason="always_close")

    async def random(topic: Topic):
        n = random.random()
        if n < 0.33:
            decision = BuyAndSellSignal.BUY
        elif n < 0.66:
            decision = BuyAndSellSignal.SELL
        else:
            decision = BuyAndSellSignal.NO

        return DealMessage(buy_and_sell=decision, reason="random")

    @staticmethod
    async def t_cross(topic: Topic):
        """
        昨日と今日で乖離が激しいと機能しなそう。
        日付変更後早いタイミングで判断が必要。
        日時実行をしないと、判断が漏れる。⇛previousなtickerを取って、乖離を確認する
        汎用的にするには、ticker_previous_t_crossを取るとデコレーションできるといい
        t_cross + limit lossを指定した場合、limit lossの領域内に戻ってくると再注文されてしまう。
        次回の注文のトリガーとして、
        """
        if topic.ticker_previous_t_cross.t_cross == 0:
            decision = BuyAndSellSignal.NO
        elif topic.ticker_previous_t_cross.t_cross == 1:
            decision = BuyAndSellSignal.BUY
        elif topic.ticker_previous_t_cross.t_cross == -1:
            decision = BuyAndSellSignal.SELL
        else:
            raise Exception()
        return DealMessage(buy_and_sell=decision, reason="t_cross")

    @staticmethod
    async def limit(topic: Topic):
        if topic.position.is_empty:
            return None

        if (topic.rule.limit or topic.rule.loss) == False:
            return None

    @staticmethod
    async def loss(topic: Topic):
        if topic.position.is_empty:
            return None

        if (topic.rule.limit or topic.rule.loss) == False:
            return None


class Decisions:
    @staticmethod
    async def default(decisions) -> Union[DealMessage, None]:
        """複数の判断から最終的な判断を生成する。現在は１要素のみの決め打ち"""
        decisions = [x for x in decisions if x.buy_and_sell != BuyAndSellSignal.NO]
        return decisions[0] if decisions else None
