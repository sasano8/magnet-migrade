from sqlalchemy.orm import Session

from ..datastore import schemas as db_schemas
from . import models, schemas
from .brokers import brokers

# class TradeDetector(GenericRepository[models.TradeDetector]):
#     pass


# class TradeProfile:
#     pass


# class TradeJob:
#     pass


class TradeResult:
    @staticmethod
    def create_from_job(db: Session, job: schemas.TradeJob):
        # obj = convert_job_to_result(job, as_back_test=False)
        # created = self.create(data=obj)
        # return created

        from ..datastore.models import CryptoTradeResult

        t = CryptoTradeResult.as_rep()
        obj = convert_job_to_result(job, as_back_test=False)
        created = t.create(db, **obj.dict())
        return created


def convert_job_to_result(
    job: schemas.TradeJob, as_back_test: bool = False
) -> db_schemas.CryptoTradeResult:
    obj = db_schemas.CryptoTradeResult(
        provider=job.provider,
        market=job.market,
        product=job.product,
        periods=job.periods,
        size=job.order_status.entry_order.amount,
        entry_date=job.order_status.entry_order.order_date,
        entry_side=job.order_status.entry_order.bid_or_ask,
        entry_price=job.order_status.entry_order.price,
        entry_commission=job.order_status.entry_order.commission,
        entry_reason=job.order_status.entry_order.comment,
        settle_date=job.order_status.settle_order.order_date,
        settle_side=job.order_status.settle_order.bid_or_ask,
        settle_price=job.order_status.settle_order.price,
        settle_commission=job.order_status.settle_order.commission,
        settle_reason=job.order_status.settle_order.comment,
        job_name=job.name,
        job_version=job.version,
        is_back_test=as_back_test,
    )
    return obj
