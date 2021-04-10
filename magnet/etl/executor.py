import inspect
from typing import Any, Callable, Coroutine, List, TypeVar

from sqlalchemy.orm import Session
from typer.models import Context

from ..commons import BulkResult, EtlJobResult
from ..database import get_db
from ..domain.datastore.models import EtlJobResult as EtlJobResultDatabase

F = TypeVar("F", bound=Callable)

daily_jobs: List[Callable[..., Coroutine[Session, Any, BulkResult]]] = []
monthly_jobs: List[Callable[..., Coroutine[Session, Any, BulkResult]]] = []
yearly_jobs: List[Callable[..., Coroutine[Session, Any, BulkResult]]] = []


async def run_daily():
    results: List[EtlJobResult] = []

    for func in daily_jobs:
        for db in get_db():
            result = await func(db)
            try:
                db.commit()
            except Exception as e:
                db.rollback()
                result.error_summary = str(e)

            if inspect.isfunction(func):
                name = func.__name__
                description = func.__doc__ or ""
            else:
                name = func.__class__.__name__
                description = func.description  # type: ignore

            if hasattr(result, "dict"):
                result_dict = result.dict()
            else:
                if result is None:
                    result_dict = {}
            results.append(
                EtlJobResult(name=name, description=description, **result_dict)
            )

    for db in get_db():
        for info in results:
            db.add(EtlJobResultDatabase(**info.dict()))

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
