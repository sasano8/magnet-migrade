import asyncio
import logging
import random
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, Iterable, List, Literal, Tuple, TypedDict, Union

from pydantic import BaseModel

from framework import DateTimeAware
from framework.scheduler import Scheduler
from pp.protocols import PCancelToken

from .interfaces import BTradePositionDeal
from .portfolio import AskBid, PositionStatus, TradePosition, VirtualAccount

logger = logging.getLogger(__name__)


class BuyAndSellSignal(str, Enum):
    NO = ""  # 何も判断材料を検知しなかった。このシグナルは後続に送信されません。
    BUY = "BUY"
    SELL = "SELL"
    CLOSE = "CLOSE"  # 持っているポジションを決済する。現在のポジションに応じて、BUYとSELLになります。もしくは、ポジションがなければ無視されます
    NOTIFY = "NOTIFY"  # 売買は行わないが、メッセージを送信したい場合に利用する
    CONFLICT = "CONFLICT"  # BUY SELL CLOSE の意思が衝突した発出されるシグナル。注文は行われず、注文データにメッセージが残ります。


# class Topic(BaseModel):
#     topic_dt: DateTimeAware
#     ticker: Any = ""
#     ticker_yesterday: Any = ""
#     rule: Any = None
#     position: TradePosition = None
#     decision: Any = None


class Topic2(TypedDict):
    name: str


class Topic(BaseModel):
    class Config:
        extra = "allow"
        validate_assignment = True

    current_dt: DateTimeAware
    topic_dt: DateTimeAware = None  # トピックが対象とする日時　この日時が同じ場合変換なしとみなす
    ticker: Any = None
    ticker_latest_t_cross: Any = None
    position: TradePosition = None
    decision: Any = None


class DealMessage(BaseModel):
    buy_and_sell: BuyAndSellSignal = BuyAndSellSignal.NO
    reason: str = ""
    priority: int = 100
    target_price: Decimal = None


class Dealer:
    """取引を行うべきか判断を行う"""

    def __init__(
        self,
        virtual_account: VirtualAccount,
        # create_decisions=None,
        analyzer_repository: Dict[str, Callable] = {},
        limitloss_repository: Dict[str, Callable] = {},
        dicision_repository: Dict[str, Callable] = {},
    ) -> None:
        self.virtual_account = virtual_account
        self.analyzer_repository = analyzer_repository
        self.limitloss_repository = limitloss_repository
        self.dicision_repository = dicision_repository
        self._decision = self.get_decision()
        self.analyzers = []
        self.pos_analyzers = []

    def is_valid(self):
        assert self.virtual_account
        assert self.analyzer_repository
        assert self.limitloss_repository
        assert self.dicision_repository
        assert self._decision
        assert self.limitloss_repository["limit"]
        assert self.limitloss_repository["loss"]

        # ポジションなし時のアナライザーが存在すること
        self.update_thinking(None)
        assert self.analyzers
        assert self.pos_analyzers is not None

    def get_decision(self):
        decision = self.virtual_account.decision
        return self.dicision_repository.get(decision, None)

    def _get_analyzers(self):
        analyzers = []
        excludes = []
        for analyzer_name in self.virtual_account.analyzers:
            func = self.analyzer_repository.get(analyzer_name)
            if func := self.analyzer_repository.get(analyzer_name, None):
                analyzers.append(func)
            else:
                excludes.append(analyzer_name)

        return (analyzers, excludes)

    def get_analyzers(self):
        analyzers, excludes = self._get_analyzers()
        if excludes:
            raise Exception(excludes)
        return analyzers

    def update_thinking(self, position: Union[TradePosition, None]):
        """
        エントリーとクローズロジックを追加する
        ポジションがあれば、リミットロスの判定処理を追加する
        """

        analyzers = self.get_analyzers()
        pos_analyzers = []

        if (
            position is None or position.is_completed or position.is_cancelled
        ) == False:
            if position.limit_price is not None:
                pos_analyzers.append(self.limitloss_repository["limit"])

            if position.loss_price is not None:
                pos_analyzers.append(self.limitloss_repository["loss"])

        self.analyzers = analyzers
        self.pos_analyzers = pos_analyzers

    def get_analyzer_names(self):
        return list(x.__name__ for x in self.analyzers)

    async def analyze(self, topic):
        """トピックに対する判断を行う"""
        decisions = []
        for analyzer in self.analyzers:
            decisions.append(await analyzer(topic))
        return decisions

    async def pos_analyze(self, position):
        """トピックに対する判断を行う"""
        decisions = []
        for analyzer in self.pos_analyzers:
            decisions.append(await analyzer(position))
        return decisions

    @staticmethod
    def filter_decisions(decisions) -> List[DealMessage]:
        filterd = []
        for x in decisions:
            if not x:
                continue
            assert isinstance(x, DealMessage)
            if (
                x.buy_and_sell == BuyAndSellSignal.NO
                or x.buy_and_sell == BuyAndSellSignal.NOTIFY
            ):
                continue
            filterd.append(x)

        return filterd

    async def decision(self, topic) -> DealMessage:
        """ブローカに注文出すための意思表示を行う"""
        if topic is None:
            return None
        decisions = await self.analyze(topic)
        filterd = self.filter_decisions(decisions)
        decision = await self._decision(filterd)
        return decision


def dummy_get_db():
    yield {}


class Broker:
    """１つのトピックに対する取引操作を提供する"""

    def __init__(
        self,
        position,
        budget: Decimal = Decimal("0"),
        topic=None,
        virtual_account: VirtualAccount = None,
        get_db=dummy_get_db,
    ) -> None:
        self.virtual_account = virtual_account
        self.position = position
        self.budget = budget
        self._get_db = get_db

    # async def create_topic(self, close_time_or_every_second) -> Topic:
    #     # TODO: start_timeを渡すようにしたので修正すること

    #     ticker = Ticker(
    #         close_time=close_time_or_every_second,
    #         open_price=0,
    #         high_price=0,
    #         low_price=0,
    #         close_price=0,
    #         volume=0,
    #         quote_volume=0,
    #     )
    #     return Topic(
    #         topic_dt=close_time_or_every_second, position=self.position, ticker=ticker
    #     )

    @property
    def get_db(self):
        return self._get_db

    async def fetch_order_until_complete(self) -> Union[TradePosition, None]:
        if self.virtual_account.position_id is None:  # type: ignore
            return None

        try:
            position = await self.wait_until_contracted(
                self.virtual_account.position_id  # type: ignore
            )
            assert position is not None

        except Exception as e:
            logger.exception(e, exc_info=True)
            return e

        return position

    async def wait_until_contracted(self, position_id: int):
        for db in self.get_db():
            order = await self.get_order(db, position_id)
            if order.status == PositionStatus.READY:
                order = await self.order_ready_to_requested(order)

            if order.status != PositionStatus.REQUESTED:
                logger.warn(
                    f"order.id ={order.id} status = {str(order.status)}:  APIプロバイダーで注文が受理され、まだ約定が確認してない状態ですが、想定するステータスが異なります。"
                )

        status: PositionStatus = None
        while status != PositionStatus.CONTRACTED:
            for db in self.get_db():
                order = await self.get_order(db, position_id)
                if order.status == PositionStatus.REQUESTED:
                    order = await self.order_requested_to_contracted(order)
                if order.status == PositionStatus.CONTRACTED:
                    return order
                if status == PositionStatus.CANCELE_REQUESTED:
                    raise NotImplementedError()
                if status == PositionStatus.CANCELED:
                    raise NotImplementedError()

            await asyncio.sleep(5)

        raise Exception("注文が必ずリターンされるように実装されていません。")

    async def book_order(self, decision) -> Tuple[VirtualAccount, TradePosition]:
        """注文を予約します。この処理はDBへ注文の仮登録を行います。"""
        for db in self.get_db():
            virtualaccount, position = await self.order_to_ready(db, None, None)

        return (virtualaccount, position)

    async def order_to_ready(
        self, db, virtual_account, decision
    ) -> Union[VirtualAccount, TradePosition]:
        """
        READY状態の注文をデータベースに登録してください。ここでは計画だけで外部APIに注文を出さないでください。
        キャンセル処理の実装が不可能に近いため、成行で注文してください。
        この処理は、注文レコードが作成されていることと、、virtual_ccountが監視する最新の注文idが更新されていることを想定しています。
        """
        pass

    async def get_order(self, db, position_id: int) -> TradePosition:
        pass

    async def order_ready_to_requested(self, order: TradePosition):
        """apiに発注し、受理されていたらREQUESTEDをマークしてください。apiの受注番号等をapi_dataに保存してください。"""
        pass

    async def order_requested_to_contracted(self, order: TradePosition):
        """apiに注文状況を照会し、全て約定したらCONTRACTEDをマークしてください。"""
        pass

    # キャンセル処理激務むず
    # キャンセルの実装は諦める
    async def order_to_cancel_ready(self, order: TradePosition):
        """単に、CANCEL_READYをマークしてください。"""
        pass

    async def order_to_cancel_requested(self, order: TradePosition):
        """CANCELE_REQUESTEDをマークしてください。"""
        pass

    async def order_to_canceled(self, position_id: int, order: TradePosition):
        """キャンセルが完了したら、CANCELEDをマークしてください。"""
        pass

    async def get_new_topic(self, start_time_or_every_second):
        # ticker = Ticker(
        #     close_time=close_time_or_every_second,
        #     open_price=0,
        #     high_price=0,
        #     low_price=0,
        #     close_price=0,
        #     volume=0,
        #     quote_volume=0,
        # )
        # return Topic(
        #     topic_dt=close_time_or_every_second, position=self.position, ticker=ticker
        # )

        topic = await self.get_topic(Topic(current_dt=start_time_or_every_second))
        if topic is not None:
            assert topic.current_dt is not None
            assert topic.topic_dt is not None
        return topic

    # override
    async def get_topic(self, topic: Topic) -> Topic:
        topic.topic_dt = topic.current_dt
        return topic

    def log_fail(self, message):
        print("ERROR:" + str(message))

    def log_warning(self, message):
        print("WARN:" + str(message))


class MarketStream:
    """
    市場の流れとは、時間の流れ（スケジューラ）と、その時空の情報（トピック）から、取引判断を行う者（トレーダー）により構成される。
    トレーダーは、１つポジションを持ち、１つのトピックのみ観察することができる。
    """

    def __init__(
        self,
        scheduler: Scheduler = None,
        broker: Broker = None,
        # create_decisions=None,
        # make_decision=None,
        dealer: Dealer = None,
    ) -> None:
        self.broker = broker
        self.scheduler = scheduler
        self.dealer = dealer
        # self._make_decision = make_decision

    async def make_decision(self, decisions) -> Union[DealMessage, None]:
        filterd = []
        for x in decisions:
            if not x:
                continue
            assert isinstance(x, DealMessage)
            if x.buy_and_sell == BuyAndSellSignal.NO:
                continue
            filterd.append(x)

        return self._make_decision(filterd)

    async def run(self, cancel_token: PCancelToken):
        scheduler = self.scheduler.__aiter__()  # type: ignore
        dealer: Dealer = self.dealer  # type: ignore
        broker: Broker = self.broker  # type: ignore

        retry = 0

        while True:
            if cancel_token.is_canceled:
                return

            if retry > 10:
                raise Exception()

            try:
                position = await broker.fetch_order_until_complete()
            except Exception as e:
                logger.exception(e, exc_info=True)
                await asyncio.sleep(10)
                retry += 1
                continue

            try:
                d = await scheduler.__anext__()
            except StopAsyncIteration:
                break

            try:
                topic = await broker.get_new_topic(d)
            except Exception as e:
                logger.exception(e, exc_info=True)
                await asyncio.sleep(10)
                retry += 1
                continue

            retry = 0

            if topic is None:
                continue
            dealer.update_thinking(position)
            decision = await dealer.decision(topic)
            new_topic = topic.copy(deep=True, update={"decision": decision})
            yield new_topic
            if not decision:
                continue

            try:
                await broker.book_order(decision)
            except Exception as e:
                logger.exception(e, exc_info=True)
                await asyncio.sleep(10)

    async def __call__(self, cancel_token: PCancelToken):
        async for topic in self.run(cancel_token):
            pass

    async def debug(self, cancel_token: PCancelToken):
        topic_log = []
        async for topic in self.run(cancel_token):
            topic_log.append(topic.dict())
        return topic_log


class Ticker(BaseModel):
    close_time: DateTimeAware
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    quote_volume: Decimal

    t_sma_5: Decimal = 0
    t_sma_10: Decimal = 0
    t_sma_15: Decimal = 0
    t_sma_20: Decimal = 0
    t_sma_25: Decimal = 0
    t_sma_30: Decimal = 0
    t_sma_200: Decimal = 0
    t_cross: int = 0  # 1=golden cross -1=dead cross 0=no
