# type: ignore
import asyncio
from decimal import Decimal

import pytest

from framework import DateTimeAware
from framework.scheduler import Scheduler
from pytrade.algorithms import Algorithms
from pytrade.builder import MarketStreamBuilder
from pytrade.interfaces import BTradePositionDeal, BVirtualAccount
from pytrade.portfolio import Account, AskBid, TradePosition, VirtualAccount
from pytrade.stream import Broker, BuyAndSellSignal, Dealer, MarketStream


def test_empty():
    """空のバーチャルアカウントの場合streamを取得できないこと"""
    builder = MarketStreamBuilder(VirtualAccount())
    with pytest.raises(AssertionError):
        stream, token = builder.get_stream(mode="test")


def test_dealer_get_update_unalyzers_has_analyzers():
    analyzers = MarketStreamBuilder.__analyzers__

    assert list(analyzers) == [
        "random",
        "t_cross",
    ]

    # アカウントにanalyzer設定がない場合は空のanalyzerが返る
    va = VirtualAccount()
    position = None
    assert not va.analyzers
    assert not position
    dealer = Dealer(va, analyzer_repository=analyzers)
    assert not dealer.analyzers
    assert dealer.get_analyzer_names() == []
    dealer.update_thinking(None)
    assert dealer.get_analyzer_names() == []

    # 設定したanalyzerが返る
    dealer = Dealer(VirtualAccount(analyzers=["random"]), analyzer_repository=analyzers)
    assert not dealer.analyzers
    dealer.update_thinking(None)
    assert dealer.get_analyzer_names() == ["random"]

    # 設定したanalyzerが返る
    dealer = Dealer(
        VirtualAccount(analyzers=["t_cross"]), analyzer_repository=analyzers
    )
    assert not dealer.analyzers
    dealer.update_thinking(None)
    assert dealer.get_analyzer_names() == ["t_cross"]

    # 設定したanalyzerが返る（複数の場合）
    dealer = Dealer(
        VirtualAccount(analyzers=["t_cross", "random"]), analyzer_repository=analyzers
    )
    assert not dealer.analyzers
    dealer.update_thinking(None)
    assert dealer.get_analyzer_names() == ["t_cross", "random"]


def test_dealer_get_update_unalyzers_has_limitloss():
    # リミットロスを設定しない場合はanalyzerに設定されない
    analyzers = MarketStreamBuilder.__analyzers__
    limitloss = MarketStreamBuilder.__limitloss__
    dealer = Dealer(VirtualAccount(), limitloss_repository=limitloss)
    dealer.update_thinking(BTradePositionDeal(ask_or_bid=AskBid.ASK))
    assert dealer.get_analyzer_names() == []

    # リミットを設定した場合はanalyzerに設定される
    dealer = Dealer(VirtualAccount(), limitloss_repository=limitloss)
    dealer.update_thinking(
        BTradePositionDeal(ask_or_bid=AskBid.ASK, limit_price=Decimal("0"))
    )
    assert dealer.get_analyzer_names() == ["limit"]

    # ロスを設定した場合はanalyzerに設定される
    dealer = Dealer(VirtualAccount(), limitloss_repository=limitloss)
    dealer.update_thinking(
        BTradePositionDeal(ask_or_bid=AskBid.ASK, loss_price=Decimal("0"))
    )
    assert dealer.get_analyzer_names() == ["loss"]


def test_dealer_init_decision():
    decisions = MarketStreamBuilder.__decisions__

    dealer = Dealer(VirtualAccount())
    assert not dealer._decision

    dealer = Dealer(VirtualAccount(), dicision_repository=decisions)
    assert dealer._decision


def test_dealer_is_valid():
    """最低でも１つロジックがなければ不正であること"""
    analyzers = MarketStreamBuilder.__analyzers__
    limitloss = MarketStreamBuilder.__limitloss__
    decisions = MarketStreamBuilder.__decisions__

    dealer = Dealer(
        VirtualAccount(),
        analyzer_repository=analyzers,
        limitloss_repository=limitloss,
        dicision_repository=decisions,
    )
    with pytest.raises(Exception):
        dealer.is_valid()

    dealer = Dealer(
        VirtualAccount(analyzers=["random"]),
        analyzer_repository=analyzers,
        limitloss_repository=limitloss,
        dicision_repository=decisions,
    )
    dealer.is_valid()


def test_dealer_decision():
    analyzers = {"always_buy": Algorithms.always_buy}
    limitloss = MarketStreamBuilder.__limitloss__
    decisions = MarketStreamBuilder.__decisions__

    dealer = Dealer(
        VirtualAccount(analyzers=["always_buy"]),
        analyzer_repository=analyzers,
        limitloss_repository=limitloss,
        dicision_repository=decisions,
    )

    # topicがNoneの時は判断されません
    dealer.update_thinking(None)
    result = asyncio.run(dealer.decision(None))
    assert result is None

    # 何かトピックが渡されたら常にbuyが返ること
    dealer.update_thinking(None)
    result = asyncio.run(dealer.decision(1))
    assert result.buy_and_sell == BuyAndSellSignal.BUY


def test_aaaaaaaaaaaaa():
    scheduler = Scheduler([DateTimeAware(2015, 1, x) for x in range(1, 32)])

    stream = MarketStream(
        scheduler=scheduler,
        broker=Broker(TradePosition(), budget=Decimal("1000") * 1000),
        create_decisions=(Algorithms.decision_random, Algorithms.decision_random),
        make_decision=make_decision,
    )

    decision_log = asyncio.run(stream.debug(1))
    assert len(decision_log) == 31


def test_zaif():
    stream, token = MarketStreamBuilder(
        BVirtualAccount(
            product="btcjpy", periods=1, analyzers=["always_buy", "always_close"]
        )
    ).get_stream(mode="test")

    result = asyncio.run(stream.debug(token))
    # assert result == 1

    import devtools

    devtools.debug(result)

    # name: str = ""
    # allocation_rate: Decimal = Field(0, ge=0, le=1, description="物理口座内の割合。")
    # allocated_margin: Decimal = Field(
    #     0,
    #     ge=0,
    #     description="証拠金（資金）。reallocationを行った際に、rateと整合性が取れる。",
    # )
    # product: str = ""
    # periods: int = 60 * 60 * 24
    # analyzers: List[str] = []
    # decision: str = "default"
    # ask_limit_rate: Decimal = Field(0, ge=0)
    # ask_loss_rate: Decimal = Field(0, ge=0)
    # bid_limit_rate: Decimal = Field(0, ge=0)
    # bid_loss_rate: Decimal = Field(0, ge=0)

    # # system
    # id: int = None
    # user_id: int = None
    # trade_account_id: int = None
    # version: int = 0
    # description: str = ""
    # position: TradePosition = None
