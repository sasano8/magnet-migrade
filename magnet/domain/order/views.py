from fastapi import Depends

from pandemic import APIRouter

from ...database import get_db
from . import usecase as uc

router = APIRouter()


@router.get("/capability")
async def get_capabilities():
    action = uc.GetCapability()
    return action.do()


@router.post("/bot")
async def create_bot(db=Depends(get_db), *, profile: uc.CreateTradeBot):
    return profile.do(db)


@router.get("/bot/{profile_id}")
async def get_bot(profile_id: int, db=Depends(get_db)):
    action = uc.GetBotProfile(profile_id=profile_id)
    return action.do(db)




@router.post("/bot/{profile_id}/switch", description="BotのOnOffを切り替えます。")
async def switch_bot(profile_id: int, is_active: bool, db=Depends(get_db)):
    action = uc.ScheduleBot(profile_id=profile_id)
    return action.switch(db, is_active=is_active)


@router.get("/bot/{profile_id}/deal", description="BOTに自動売買させる。テスト用")
async def deal_bot(profile_id: int, db=Depends(get_db)):
    action = uc.ScheduleBot(profile_id=profile_id)
    return await action.deal(db)
