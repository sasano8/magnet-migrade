from fastapi import Depends

from pandemic import APIRouter

from ...database import get_db
from . import usecase as uc

router = APIRouter()


@router.get("/capability")
async def get_capabilities():
    action = uc.GetCapability()
    return action.do()


@router.post("/profile")
async def create_bot(db=Depends(get_db), *, profile: uc.CreateTradeBot):
    return profile.do(db)


@router.get("/profile/{profile_id}")
async def get_bot(profile_id: int, db=Depends(get_db)):
    action = uc.GetBotProfile(profile_id=profile_id)
    return action.do(db)


@router.post("/profile/{profile_id}/switch", description="BotのOnOffを切り替えます。")
async def switch_bot(profile_id: int, is_active: bool, db=Depends(get_db)):
    action = uc.ScheduleBot(profile_id=profile_id)
    return action.switch(db, is_active=is_active)


@router.get("/profile/{profile_id}/deal", description="BOTに自動売買させる。テスト用")
async def deal_bot(profile_id: int, db=Depends(get_db)):
    action = uc.ScheduleBot(profile_id=profile_id)
    return await action.deal(db)


@router.post("/etl/load_all")
async def load_all():
    """株・為替・暗号通貨等のデータを最新化する"""
    from ...etl import run_daily

    result = await run_daily()
    return result
