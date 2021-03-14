from typing import Any, Callable, Coroutine, List, TypeVar

from sqlalchemy.orm import Session

from ..commons import BulkResult, TaskResult
from ..database import get_db

F = TypeVar("F", bound=Callable)

daily_jobs: List[Callable[..., Coroutine[Session, Any, BulkResult]]] = []
monthly_jobs: List[Callable[..., Coroutine[Session, Any, BulkResult]]] = []
yearly_jobs: List[Callable[..., Coroutine[Session, Any, BulkResult]]] = []


async def run_daily():
    results: List[TaskResult] = []

    for func in daily_jobs:
        for db in get_db():
            result = await func(db)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                result.error_summary = str(e)

            results.append(TaskResult(name=func.__name__, **result.dict()))

    return results


def daily(func: F) -> F:
    daily_jobs.append(func)
    return func


def monthly(func: F) -> F:
    monthly_jobs.append(func)
    return func


def yearly(func: F) -> F:
    yearly_jobs.append(func)
    return func
