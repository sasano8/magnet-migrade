import asyncio
import datetime
import logging
from typing import Any, Callable, Coroutine, List, Literal, Union

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.encoders import SetIntStr

import pandemic
from framework import DateTimeAware
from libs.fastapi import build_exception

from ...commons import BaseModel, BulkResult, PagenationQuery
from ...database import Session, get_db
from ..datastore.models import CryptoTradeResult
from . import algorithms, crud, models, schemas
from .core import interfaces

brokers = crud.brokers

logger = logging.getLogger(__name__)

# router = APIRouter()
router = pandemic.APIRouter()

TradeProfileService = models.TradeProfile.as_service()
TradeJobService = models.TradeJob.as_service()


class TradeProfileView:
    @staticmethod
    @router.get("/template")
    async def index(
        q: PagenationQuery, db: Session = Depends(get_db)
    ) -> List[schemas.TradeProfile]:
        return TradeProfileService.index(db, skip=q.skip, limit=q.limit)

    @staticmethod
    @router.post("/template")
    async def create(
        data: schemas.TradeProfileCreate, db: Session = Depends(get_db)
    ) -> schemas.TradeProfile:
        obj = models.TradeProfile.Q_get_by_name(db, name=data.name)
        if obj:
            e = build_exception(
                status_code=422,
                loc=("name",),
                msg="すでに同名のテンプレートが存在します。",
            )
            raise e
        return TradeProfileService.create(db, **data.dict())

    @staticmethod
    @router.get("/template/{id}")
    async def get(id: int, db: Session = Depends(get_db)) -> schemas.TradeProfile:
        return TradeProfileService.get(db, id=id)

    @staticmethod
    @router.delete("/template/{id}/delete", status_code=200)
    async def delete(id: int, db: Session = Depends(get_db)) -> int:
        return TradeProfileService.delete(db, id=id)

    @staticmethod
    @router.patch("/template/{id}/patch")
    async def patch(
        id: int, data: schemas.TradeProfilePatch, db: Session = Depends(get_db)
    ) -> schemas.TradeProfile:
        return TradeProfileService.patch(db, **dict(data.dict(), id=id))

    @staticmethod
    @router.post("/template/{id}/copy_as_worker")
    async def copy_as_worker(
        id: int,
        as_job_name: str,
        as_job_type: Literal["production", "virtual", "backtest"],
        db: Session = Depends(get_db),
    ) -> schemas.TradeJob:
        obj = TradeProfileService.get(db, id=id)
        if not obj:
            raise HTTPException(status_code=404, detail=f"id:{id} not found.")
        job = schemas.TradeJob.from_orm(obj)
        job.name = as_job_name
        job.job_type = as_job_type
        data = schemas.TradeProfileCreate(
            **job.dict(exclude={"id", "last_check_date", "order_status"})
        )
        created = await TradeJobView.create(db=db, data=data)
        return created


class TradeJobView:
    @staticmethod
    @router.get("/worker")
    async def index(
        q: PagenationQuery, db: Session = Depends(get_db)
    ) -> List[schemas.TradeJob]:
        return TradeJobService.index(db, skip=q.skip, limit=q.limit)

    @staticmethod
    @router.post("/worker")
    async def create(
        data: schemas.TradeProfileCreate, db: Session = Depends(get_db)
    ) -> schemas.TradeJob:
        obj = models.TradeJob.Q_get_by_name(db, name=data.name)
        if obj:
            e = build_exception(
                status_code=422,
                loc=("name",),
                msg="すでに同名のテンプレートが存在します。",
            )
            raise e
        return TradeJobService.create(db, **data.dict())

    @staticmethod
    @router.get("/worker/{id}", response_model=schemas.TradeJob)
    async def get(id: int, db: Session = Depends(get_db)) -> schemas.TradeJob:
        return TradeJobService.get(db, id=id)

    @staticmethod
    @router.delete("/worker/{id}/delete", status_code=200)
    async def delete(id: int, db: Session = Depends(get_db)) -> int:
        return TradeJobService.delete(db, id=id)

    @staticmethod
    @router.patch("/worker/{id}/patch")
    async def patch(
        id: int, data: schemas.TradeProfilePatch, db: Session = Depends(get_db)
    ) -> schemas.TradeJob:
        return TradeJobService.patch(db, **dict(data.dict(), id=id))

    @staticmethod
    @router.post("/worker/{id}/reset_order_status")
    async def reset_order_status(
        id: int, db: Session = Depends(get_db)
    ) -> schemas.TradeJob:
        obj = TradeJobService.get(db, id=id)
        data = schemas.TradeJob.from_orm(obj)
        data.order_status = None
        data.last_check_date = None
        return TradeJobService.patch(db, **data.dict())

    @staticmethod
    @router.post("/worker/{id}/exec")
    async def exec(id: int, db: Session = Depends(get_db)):
        """ジョブを実行する。last_check_dateからさかのぼってエントリーを行う。Noneの場合は、本日分よりトレードを行う。"""
        tmp = TradeJobService.get(db, id=id)
        job = schemas.TradeJob.from_orm(tmp)

        from magnet.domain.datastore import models as mymodels

        # ohlc = magnet.datastore.crud.CryptoOhlcDaily(db)
        # rep_result = crud.TradeResult(self.db)
        scheduler = []

        def create_schedule(before, until):
            if before > until:
                raise Exception()

            diff = (until - before).days
            start_day = datetime.date.today() - datetime.timedelta(days=diff)
            for day_count in range(diff):
                yield start_day + datetime.timedelta(days=day_count)

        if job.job_type == "production":
            broker = brokers.instatiate(job.broker)
            broker.sleep_interval = 10
            if job.last_check_date is None:
                scheduler = list(
                    create_schedule(datetime.date.today(), datetime.date.today())
                )
            else:
                scheduler = list(
                    create_schedule(job.last_check_date.date(), datetime.date.today())
                )
        elif job.job_type == "virtual":
            # 現在に対して仮想的にトレードを行う
            broker = brokers.instatiate(job.broker)
            broker.sleep_interval = 10
            broker = broker  # 仮想ブローカーにラップする
            if job.last_check_date is None:
                current_date = DateTimeAware.utcnow().date() - datetime.timedelta(
                    days=1
                )  # 本日はすなわち昨日のクローズタイム - 1日
                scheduler = [datetime.date.today()]
            raise NotImplementedError()
        elif job.job_type == "backtest":
            # 過去データに対してトレードを行う
            job = await TradeJobView.reset_order_status(id=job.id, db=db)
            job = schemas.TradeJob.from_orm(job)
            CryptoTradeResult.P_delete_by_job_name(db, job_name=job.name)
            broker = brokers.instatiate("backtest")
            broker.sleep_interval = 0  # 外部との通信はないので0

            # from ..datastore.crud import select_close_date_range

            # r = mymodels.CryptoOhlc.as_rep()
            # query = select_close_date_range(
            #     r.query(db),
            #     provider=job.provider,
            #     market=job.market,
            #     product=job.product,
            #     periods=job.periods,
            #     until=datetime.date.today(),
            #     order_by="asc",
            # )

            query = mymodels.CryptoOhlc.Q_select_close_date_range(
                db,
                provider=job.provider,
                market=job.market,
                product=job.product,
                periods=job.periods,
                until=datetime.date.today(),
                order_by="asc",
            )

            scheduler = [
                datetime.datetime.combine(x.close_time, datetime.time()) for x in query
            ][:-1]
            logger.info(f"{len(scheduler)}件のデータでバックテストを行います。")
        else:
            raise Exception()

        # broker.get_topic
        # broker.scheduler = scheduler
        # broker.trade_type = None
        broker.db = db
        broker.detect_signal = algorithms.detectors.get(job.detector_name)

        for dt in scheduler:
            # ジョブを更新しないと状態が更新されない
            # tmp = await self.get(id=id)
            # job = schemas.TradeJob.from_orm(tmp)
            job = await TradeJobView.stop_and_reverse(job, broker, dt, db=db)

        return job

    @staticmethod
    async def stop_and_reverse(
        job: schemas.TradeJob,
        broker,
        close_time_or_every_second,
        db: Session = Depends(get_db),
    ) -> schemas.TradeJob:
        """ドテン方式アルゴリズムを実行する"""
        check = broker.valid_currency_pair(job.product)  # 念の為有効なプロダクト名か確認

        today = close_time_or_every_second + datetime.timedelta(days=1)

        # 最新データがあるか確認
        today_topic = await broker.get_topic(db, job, today)
        if not today_topic:
            logger.warning(f"{today}のデータがありません。")
            return job

        # 昨日分のデータを取得
        topic = await broker.get_topic(db, job, close_time_or_every_second)

        # topic.t_cross = 1  # mock test
        limit_or_loss = job.detect_limit_loss(today_topic.close_price)
        if limit_or_loss:
            if job.order_status:
                if job.order_status.status == "entried":
                    job = await broker.order("settle", job, today, db)
                    await broker.notify(limit_or_loss, close_time_or_every_second)

                if job.order_status and job.order_status.status == "settled":
                    retry_count = 5
                    for i in range(retry_count):
                        await asyncio.sleep(
                            broker.sleep_interval
                        )  # 注文直後は証拠金や注文がが更新されていないため、少し時間を開ける
                        entry_order = await broker.fetch_order_result(
                            job.order_status.entry_order
                        )
                        settle_order = await broker.fetch_order_result(
                            job.order_status.settle_order
                        )
                        if (entry_order is None or settle_order is None) == False:
                            break

                    job.order_status.entry_order = entry_order
                    job.order_status.settle_order = settle_order

                    if (
                        job.order_status.entry_order.price
                        or job.order_status.settle_order.price
                    ):

                        # トレード結果を保存
                        # rep_result = crud.TradeResult(db)
                        # rep_result.create_from_job(job)
                        crud.TradeResult.create_from_job(db, job=job)

                        job.order_status = None
                        # await self.patch(id=job.id, data=job)
                        result = models.TradeJob.as_service().patch(db, **job.dict())
                    else:
                        print(1)
                        pass

        # サイン検出
        bid_or_ask = broker.detect_signal(topic)
        if bid_or_ask is None:
            return await broker.order("pass", job, today, db)  # 最終チェック日を更新

        if job.order_status:
            if job.order_status.status == "entried":
                job = await broker.order("settle", job, today, db)

        if job.order_status and job.order_status.status == "settled":
            retry_count = 5
            for i in range(retry_count):
                await asyncio.sleep(
                    broker.sleep_interval
                )  # 注文直後は証拠金や注文がが更新されていないため、少し時間を開ける
                entry_order = await broker.fetch_order_result(
                    job.order_status.entry_order
                )
                settle_order = await broker.fetch_order_result(
                    job.order_status.settle_order
                )
                if (entry_order is None or settle_order is None) == False:
                    break

            job.order_status.entry_order = entry_order
            job.order_status.settle_order = settle_order

            # トレード結果を保存
            # rep_result = crud.TradeResult(db)
            if (
                job.order_status.entry_order.price
                or job.order_status.settle_order.price
            ):
                crud.TradeResult.create_from_job(db, job=job)
                # rep_result.create_from_job(db, job=job)

                job.order_status = None
                result = models.TradeJob.as_service().patch(db, **job.dict())
                # await self.patch(id=job.id, data=job)
            else:
                print(1)
                pass

        # 発注済みなら実行しない
        if job.order_status and job.order_status.status == "entried":
            return await broker.order("pass", job, today, db)  # 最終チェック日を更新

        current_price = topic.close_price
        # current_price = broker.get_ticker()

        entry_order = interfaces.Order(
            bid_or_ask=bid_or_ask,
            order_type="market",
            time_in_force="GTC",
            currency_pair=job.product,
            # price=profile.trade_rule.entry,
            amount=job.calc_amount(current_price),
            limit=job.calc_limit(bid_or_ask, current_price),
            loss=job.calc_loss(bid_or_ask, current_price),
            comment="cross",
        )
        # 決済用注文
        settle_order = interfaces.OrderStatus.create_settle_order(entry_order)

        job.order_status = interfaces.OrderStatus(
            entry_order=entry_order,
            settle_order=settle_order,
        )

        # 新規注文
        return await broker.order("entry", job, today, db)


class Etl:
    @router.post("/etl/load_all")
    async def load_all():
        """株・為替・暗号通貨等のデータを最新化する"""
        from ...etl import run_daily

        result = await run_daily()
        return result
