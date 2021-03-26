# from .stream import BuyAndSellSignal, DealMessage, Topic
import random

from pytrade.stream import BuyAndSellSignal, DealMessage

from .abc import Analyzer
from .repository import AnalyzersRepository
from .topics import (
    CurrentTickerProvider,
    CurrentTickerTestProvider,
    YesterdayOhlcProvider,
)


@AnalyzersRepository.register
class EmptyAnalyzer(Analyzer):
    """常に何も判断しません。テスト用アルゴリズムです。"""

    _name = "empty"
    __topics__ = []

    async def __call__(self, topic):
        return None


@AnalyzersRepository.register
class AlwaysBuyAnalyzer(Analyzer):
    """常に買いの指示を送出します。これは、テスト用アルゴリズムです。"""

    _name = "always_buy"
    __topics__ = []

    async def __call__(self, topic):
        current = topic["current_ticker"]
        last_traded_price = current.ltp
        return DealMessage(
            buy_and_sell=BuyAndSellSignal.BUY,
            reason="always_buy",
            target_price=last_traded_price,
        )


@AnalyzersRepository.register
class AlwaysCloseAnalyzer(Analyzer):
    """常にクローズの指示を送出します。これは、テスト用アルゴリズムです。"""

    _name = "always_close"
    __topics__ = []

    async def __call__(self, topic):
        return DealMessage(buy_and_sell=BuyAndSellSignal.CLOSE, reason="always_close")


@AnalyzersRepository.register
class TransitionalAnalyzer(Analyzer):
    """分析が行われる度、buy sell close とシグナルを遷移させます。テストで利用します。"""

    _name = "test_buy_sell_close"
    __topics__ = []

    def __post_init__(self):
        self.count = 0

    async def __call__(self, topic):
        current = topic["current_ticker"]
        last_traded_price = current.ltp
        if self.count == 0:
            self.count += 1
            return DealMessage(
                buy_and_sell=BuyAndSellSignal.BUY,
                reason="test_buy_sell_close",
                target_price=last_traded_price,
            )
        elif self.count == 1:
            self.count += 1
            return DealMessage(
                buy_and_sell=BuyAndSellSignal.SELL,
                reason="test_buy_sell_close",
                target_price=last_traded_price,
            )
        elif self.count == 2:
            self.count = 0
            return DealMessage(
                buy_and_sell=BuyAndSellSignal.CLOSE,
                reason="test_buy_sell_close",
                target_price=last_traded_price,
            )
        else:
            raise Exception()


@AnalyzersRepository.register
class TCrossAnalyzer(Analyzer):
    """
    昨日と今日で乖離が激しいと機能しなそう。
    日付変更後早いタイミングで判断が必要。
    日時実行をしないと、判断が漏れる。⇛previousなtickerを取って、乖離を確認する
    汎用的にするには、ticker_previous_t_crossを取るとデコレーションできるといい
    t_cross + limit lossを指定した場合、limit lossの領域内に戻ってくると再注文されてしまう。
    次回の注文のトリガーとして、
    """

    _name = "t_cross"
    __topics__ = ["yesterday_ohlc"]

    async def __call__(self, topic):
        ohlc = topic["yesterday_ohlc"]
        # TODO: 最新のデータを取り込んでいない場合、Noneが返る
        # その場合、どうするべきか考える

        if ohlc.t_cross == 0:
            decision = BuyAndSellSignal.NO
        elif ohlc.t_cross == 1:
            decision = BuyAndSellSignal.BUY
        elif ohlc.t_cross == -1:
            decision = BuyAndSellSignal.SELL
        else:
            raise Exception()
        return DealMessage(
            buy_and_sell=decision, reason="t_cross", target_price=ohlc.close_price
        )
