from decimal import Decimal
from typing import List

from sqlalchemy import select

from pytrade.portfolio import AskBid, PositionStatus

from ...commons import BaseModel, intellisense
from ...database import Session
from .bot import Bot
from .models import TradeBot, TradeProfile
from .repository import AnalyzersRepository, BrokerRepository, TopicRepository


@intellisense
class CreateTradeBot(BaseModel):
    provider: str = "cryptowatch"
    market: str = "bitflyer"
    product: str = "FX_BTC_JPY"
    periods: Decimal = 60 * 60 * 24  # type: ignore
    # ask_or_bid: AskBid
    limit_rate: Decimal = None  # type: ignore
    stop_rate: Decimal = None  # type: ignore
    analyzers: List[str] = ["empty"]

    def do(self, db: Session):
        obj = TradeProfile(**self.dict())
        obj = obj.create(db)

        bot = ScheduleBot(profile_id=obj.id).create(db)
        return obj


@intellisense
class GetCapability(BaseModel):
    def do(self):
        return {
            "brokers": BrokerRepository.get_names(),
            "topics": TopicRepository.get_names(),
            "analyzers": AnalyzersRepository.get_names(),
        }


@intellisense
class GetBotProfile(BaseModel):
    profile_id: int

    def do(self, db: Session) -> TradeProfile:
        if not (obj := db.query(TradeProfile).get(self.profile_id)):
            raise Exception()

        return obj


class ScheduleBotQuery(BaseModel):
    pass


@intellisense
class ScheduleBot(BaseModel):
    profile_id: int

    def create(self, db: Session):
        bot = TradeBot(profile_id=self.profile_id, is_active=False)
        bot.create(db)
        return bot

    def get(self, db: Session):
        if not (
            bot := db.query(TradeBot)
            .filter(TradeBot.profile_id == self.profile_id)
            .one_or_none()
        ):
            raise Exception("not found.")
        return bot

    def switch(self, db: Session, is_active: bool):
        """
        BOTのスケジューリング状態を変更します。
        true - 自動売買を開始します。
        false - 保持しているポジションをクローズした上で、BOTがスケジューリングされないようにします。
        """
        bot = self.get(db)
        bot.update(db, is_active=is_active)
        return bot

    async def deal(self, db: Session):
        profile = GetBotProfile.do(self, db)
        state = self.get(db)
        bot = Bot(profile, state)
        result = await bot.deal_at_now()
        # result = await bot.deal_at_now()
        # result = await bot.deal_at_now()
        return result
