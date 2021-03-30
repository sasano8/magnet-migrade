from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, List, Literal, Set, Type, Union

from sqlalchemy.sql.expression import select

from framework import DateTimeAware

from ...database import get_db
from .abc import Analyzer, BrokerImpl, TopicProvider
from .models import TradeBot, TradeLog, TradeProfile
from .repository import AnalyzersRepository, BrokerRepository, TopicRepository
from .schemas import BuyAndSellSignal, DealMessage, PreOrder, RemainOrder, TradeResult


@dataclass
class Bot:
    profile: TradeProfile
    state: TradeBot
    broker: BrokerImpl = field(init=False)
    topics: List[TopicProvider] = field(init=False)
    analyzers: List[Analyzer] = field(init=False)

    def __post_init__(self):
        broker, topics, analyzers = self.build(self.profile)
        self.check_conflict_alias(topics)

        self.broker = broker
        self.topics = topics
        self.analyzers = analyzers

    @staticmethod
    def check_conflict_alias(topics: List[TopicProvider]):
        """トピック名が衝突していないか検証する"""
        topic_names = set()
        for topic in topics:
            if name := topic.get_alias():
                if name in topic_names:
                    raise Exception()
                else:
                    topic_names.add(name)

    @staticmethod
    def build(profile: TradeProfile):
        """profileから自動売買に必要なインスタンスを生成する"""
        # analyzer_types: Set[Type[Analyzer]] = set()
        analyzers = []
        for analyzer_name in profile.analyzers:
            # analyzer = AnalyzersRepository.get(analyzer_name=analyzer_name)
            # analyzer_types.add(analyzer)
            analyzers.append(
                AnalyzersRepository.instantiate(analyzer_name=analyzer_name)
            )

        # テスト時は仮のtickerにする
        if True:
            topic_names = set(["current_ticker"])
        else:
            topic_names = set(["test_current_ticker"])

        # for analyzer in analyzer_types:
        #     topic_names.update(analyzer.__topics__)
        for analyzer in analyzers:
            topic_names.update(analyzer.__topics__)

        broker = BrokerRepository.get(profile.market)()

        topics = []
        for topic_name in topic_names:
            factory = TopicRepository.get(topic_name)
            topics.append(factory(profile, broker))

        # analyzers = []
        # for analyzer_type in analyzer_types:
        #     analyzers.append(analyzer_type())

        return broker, topics, analyzers

    async def cancel_order(self):
        """エントリーに付属する注文（リミットストップ）をキャンセルする"""
        broker = self.broker
        profile = self.profile
        state = self.state

        # リミットストップなどの注文をキャンセルする
        # キャンセルは冪等性なので何度実行してもよい
        for db in get_db():
            entry_accepted_cancel_data = await broker.cancel(state.entry_order_accepted)

            new_state = db.execute(
                state.stmt_update(
                    entry_cancel_order_accepted=entry_accepted_cancel_data,
                ).returning(TradeBot)
            ).one()

        self.state = TradeBot(**new_state)

    async def finalize_entry_order(self):
        """エントリー注文が全て約定・キャンセルされてことを確認し、結果を確定させる"""
        broker = self.broker
        profile = self.profile
        state = self.state

        # すでにファイナライズ済みなら終了
        if state.entry_order_finalized is not None:
            return

        status_data = await broker.fetch_order_status_until_complete(
            self.state.entry_order_accepted
        )
        trade_result = await broker.finalize(status_data)
        for db in get_db():
            new_state = db.execute(
                state.stmt_update(
                    entry_order_finalized=trade_result,
                ).returning(TradeBot)
            ).one()
            state = new_state

        self.state = TradeBot(**new_state)

    async def finalize_counter_order(self):
        """カウンター注文が全て約定・キャンセルされてことを確認し、結果を確定させる"""
        broker = self.broker
        profile = self.profile
        state = self.state

        # すでにファイナライズ済みなら終了
        if state.counter_order_finalized is not None:
            return

        status_data = await broker.fetch_order_status_until_complete(
            self.state.counter_order_accepted
        )
        trade_result = await broker.finalize(status_data)
        for db in get_db():
            new_state = db.execute(
                state.stmt_update(
                    counter_order_finalized=trade_result,
                ).returning(TradeBot)
            ).one()
            state = new_state

        self.state = TradeBot(**new_state)

    def get_remain(self) -> Union[PreOrder, None]:
        state = self.state

        # finalizedされていたら残は無しとみなす
        if state.finalized:
            return None

        # 反対売買が実施済みなら残は無しとみなす
        if state.counter_order_accepted:
            return None

        # 未決済ポジションがなければ終了
        remain = TradeResult.parse_obj(state.entry_order_finalized).get_remain()
        return remain

    async def finalize(self):
        """エントリー注文とカウンター注文をマージし、ファイナライズを更新する。"""
        state = self.state
        broker = self.broker

        entry_order_finalized = state.entry_order_finalized
        counter_order_finalized = state.counter_order_finalized

        result = TradeResult.merge_from_dict(
            entry_order_finalized, counter_order_finalized
        )
        for db in get_db():
            new_state = db.execute(
                state.stmt_update(finalized=result).returning(TradeBot)
            ).one()
            state = new_state

        self.state = TradeBot(**new_state)

    def record_trade_and_clear_state(self):
        """トレード結果をDBに登録する"""
        state = self.state
        finalized = TradeResult.parse_obj(state.finalized)

        if state.entry_side == 1:
            entry = finalized.buy
            counter = finalized.sell

        elif state.entry_side == -1:
            entry = finalized.sell
            counter = finalized.buy
        else:
            raise Exception()

        kwargs = dict(
            side=state.entry_side,
            size=finalized.size,
            entry_at=state.entry_at,
            counter_at=state.counter_at,
            entry_price=entry.average_price,
            entry_commission=entry.total_commission,
            entry_other_commission=entry.other_commission,
            entry_reason="",  # TODO:
            counter_price=counter.average_price,
            counter_commission=counter.total_commission,
            counter_other_commission=counter.other_commission,
            counter_reason="",  # TODO:
        )

        log = TradeLog(
            profile_version=1,  # TODO:
            profile_id=state.profile_id,
            profile_name="",  # TODO:
            is_back_test=False,  # TODO:
            provider="cryptowatch",  # TODO:
            market="bitflyer",  # TODO:
            product=state.product_code,
            periods=60 * 60 * 24,  # TODO:
            **kwargs,
        )
        log.update_properties()

        for db in get_db():
            log = log.create(db)
            new_state = db.execute(state.stmt_reset().returning(TradeBot)).one()

        self.state = TradeBot(**new_state)

    async def entry_order(self, order: PreOrder, current_dt: DateTimeAware):
        """
        ブローカーに注文を依頼し、受理レスポンスをエントリー売買として記録する。
        """
        if order.size == 0:
            return

        state = self.state
        localized_order = self.broker.localize_order(order)

        from sqlalchemy import insert

        from .models import TradeOrder

        for db in get_db():
            accepted_data = await self.broker.order(localized_order)

            values = state.dict()
            del values["id"]
            values["product_code"] = order.product_code
            values["entry_at"] = current_dt
            values["entry_order"] = order.dict()
            values["entry_order_accepted"] = accepted_data

            stmt = insert(TradeOrder).values(
                **values,
            )
            new_state = db.execute(stmt)

        # self.state = TradeBot(**new_state)  # 投げっぱなしなので状態として管理しない

    async def entry_order_continuous(self, order: PreOrder, current_dt: DateTimeAware):
        """
        ブローカーに注文を依頼し、受理レスポンスをエントリー売買として記録する。
        また、その注文をドテン売買など連続的な注文として扱う。
        """
        if order.size == 0:
            return

        state = self.state
        localized_order = self.broker.localize_order(order)

        for db in get_db():
            accepted_data = await self.broker.order(localized_order)
            # accepted_data = {}
            new_state = db.execute(
                state.stmt_reset()
                .values(
                    product_code=order.product_code,
                    entry_at=current_dt,
                    entry_order=order.dict(),
                    entry_order_accepted=accepted_data,
                )
                .returning(TradeBot)
            ).one()

        self.state = TradeBot(**new_state)

    async def counter_order(self, order: PreOrder, current_dt: DateTimeAware):
        """ブローカーに注文を依頼し、受理レスポンスを反対売買として記録する"""
        state = self.state
        localized_order = self.broker.localize_order(order)
        counter_order_accepted = await self.broker.order(localized_order)
        self.record_counter_order(localized_order, counter_order_accepted, current_dt)

    def record_counter_order(
        self, localized_order, counter_order_accepted, current_dt: DateTimeAware
    ):
        state = self.state
        for db in get_db():
            new_state = db.execute(
                state.stmt_update(
                    counter_at=current_dt,
                    counter_order=localized_order,
                    counter_order_accepted=counter_order_accepted,
                ).returning(TradeBot)
            ).one()
            state = new_state

        self.state = TradeBot(**new_state)

    def finalize_counter_order_as_empty(
        self, product_code: str, current_dt: DateTimeAware
    ):
        state = self.state
        product_code_localized = self.broker.localize_product_code(product_code)

        # ファイナライズ済みなら終了
        if state.counter_order_finalized:
            return

        # カウンターオーダー発注済みなら終了
        if state.counter_order_accepted:
            return

        result = TradeResult(product_code_localized=product_code_localized)

        for db in get_db():
            new_state = db.execute(
                state.stmt_update(
                    counter_at=current_dt,
                    counter_order_finalized=result.dict(),
                ).returning(TradeBot)
            ).one()
            state = new_state

        self.state = TradeBot(**new_state)

    async def get_topics(self, curretn_dt: DateTimeAware):
        topics = {}
        for topic in self.topics:
            result = await topic.get_topic(curretn_dt)
            topics[topic.get_alias()] = result

        return topics

    async def analyze_topics(self, topics) -> Union[DealMessage, None]:
        decisons = []
        for analyze in self.analyzers:
            result = await analyze(topics)
            decisons.append(result)

        # NoneやNoなど不要なメッセージを除去する
        filterd_decisions = self.filter_decisions(decisons)
        decision = self.make_decision(filterd_decisions)

        return decision

    async def deal_at_now(self):
        """現在時刻の文脈で取引を行う。"""
        return await self.deal_at(DateTimeAware.utcnow())

    async def deal_at(self, curretn_dt: DateTimeAware):
        """指定した時刻の文脈で取引を行う。通常はdealを使用する。バックテストの時に時刻を指定する。"""

        topics = await self.get_topics(curretn_dt)
        decision = await self.analyze_topics(topics)
        if not decision:
            return None

        return await self.trade(curretn_dt, decision)

    async def trade(self, current_dt: DateTimeAware, decision: DealMessage):
        broker = self.broker
        profile = self.profile
        state = self.state

        if decision.buy_and_sell == BuyAndSellSignal.BUY:
            side = 1
        elif decision.buy_and_sell == BuyAndSellSignal.SELL:
            side = -1
        elif decision.buy_and_sell == BuyAndSellSignal.CLOSE:
            side = 0
        else:
            raise NotImplementedError()

        # test OK
        # 同じ方向のポジションはすでに保持しているとみなし終了
        if state.entry_side == side:
            return

        if not state.is_empty:

            await self.cancel_order()
            await self.finalize_entry_order()
            remain = self.get_remain()
            if remain:
                counter_order = PreOrder(
                    product_code=state.product_code,
                    side=remain.side * -1,
                    target_price=decision.target_price,
                    size=remain.size,
                    limit_rate=None,
                    stop_rate=None,
                )

                await self.counter_order(counter_order, current_dt)
            else:
                if not self.state.counter_order_finalized:
                    self.finalize_counter_order_as_empty(state.product_code, current_dt)

            await self.finalize_counter_order()
            await self.finalize()
            self.record_trade_and_clear_state()

        # 新たな文脈のトレードを行う場合は、常にエンプティな状態を前提とする
        state = self.state
        assert state.is_empty

        # シグナルがクローズなら終了（ポジションを持っていない状態になればよい）
        if side == 0:
            return

        size = PreOrder.calc_amount(
            budget=profile.margin,
            price=decision.target_price,
            min_unit=Decimal("0.01"),  # TODO: budgetをprofileにもたせる
        )

        if side == 1:
            limit_rate = profile.ask_limit_rate
            stop_rate = profile.ask_stop_rate
        elif side == -1:
            limit_rate = profile.bid_limit_rate
            stop_rate = profile.bid_stop_rate
        else:
            raise Exception()

        order = PreOrder(
            product_code=profile.product,
            side=side,
            target_price=decision.target_price,
            size=size,
            limit_rate=limit_rate,
            stop_rate=stop_rate,
            # limit_rate=1.2,
            # stop_rate=0.9,
        )

        if state.is_stop_reverse:
            await self.entry_order_continuous(order, current_dt)
        else:
            await self.entry_order(order, current_dt)

        print(self.state)

    @staticmethod
    def make_decision(decisions) -> Union[DealMessage, None]:
        """複数の判断から最終的な判断を生成する。現在は１要素のみの決め打ち"""
        decisions = [x for x in decisions if x.buy_and_sell != BuyAndSellSignal.NO]
        return decisions[0] if decisions else None

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
