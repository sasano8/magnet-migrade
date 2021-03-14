from typing import List

from fastapi import Depends, HTTPException, Query
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

from ...database import Session, get_db
from . import events

# from magnet.message.schemas import RFC7807


router = InferringRouter()


from pydantic import BaseModel, validator


class Dummy(BaseModel):
    name: str

    @validator("name")
    def valid_name(cls, v):
        if len(v) == 0:
            raise ValueError("長さ0だよ")
        else:
            return v

    @validator("name")
    def valid_name2(cls, v):
        if len(v) == 0:
            raise ValueError("長さ0だよ")
        else:
            return v


@cbv(router)
class SystemView:
    db: Session = Depends(get_db)

    @router.get("/statistics")
    async def get_statistics(self, filter_module: str = "backend/app"):
        """メモリ使用状況を可視化します。"""
        diff_size, total_size, str_stats = events.get_statistics()

        if filter_module == "":
            pass
        else:
            str_stats = list(filter(lambda x: filter_module in x, str_stats))

        return {
            "diff_size(MB)": diff_size,
            "total_size(MB)": total_size,
            "stats": str_stats,
        }

    @router.get("/requirement_definition")
    async def requirement_definition(
        self,
        domain: str = Query("internal", description="社内向けですか？世界に公開するサービスですか。"),
        timezone: str = Query("utc", description="utc以外のタイムゾーンを取り扱いますか。"),
        has_timezone: bool = Query(False, description="現地時間の情報を個別に保持したい要件がありますか。"),
        most_old_year: int = Query(1905, description="システムで取り扱うことを想定している一番古い日付は何年ですか。"),
        scraping: bool = Query(False, description="スクレイピングを用いる要件はありますか。"),
        etl: bool = Query(False, description="ETLの要件はありますか。"),
    ):
        """簡易的なヒアリングから、システム構築難易度を算出します"""

        difficulty = dict(
            domain=30 if domain != "internal" else 0,
            timezone=50 if timezone != "utc" else 0,
            has_timezone=50 if has_timezone else 0,
            most_old_year=100 if most_old_year < 1905 else 0,
            scraping=10 if scraping else 0,
            etl=10 if etl else 0,
        )

        sum_difficulty = sum(difficulty.values())

        return dict(sum=sum_difficulty, difficulty=difficulty)

    # @router.post("/exception_test", responses=RFC7807)
    @router.post("/exception_test")
    async def exception_test(self, dummy: Dummy):
        raise ValueError("invalid name")


#
# @app.post("/system/exception_test", response_model=RFC7807)
# async def exception_test(self, dummy: Dummy):
#     raise ValueError("invalid name")
