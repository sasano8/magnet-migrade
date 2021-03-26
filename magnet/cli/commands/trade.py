import asyncio
import functools
import signal
from typing import Callable, List, TypeVar

import typer
from sqlalchemy.sql.sqltypes import Date

from framework import DateTimeAware, undefined

from ...database import get_db

F = TypeVar("F", bound=Callable)

app = typer.Typer()


def inject(**kwargs):
    if not len(kwargs) == 1:
        raise Exception()

    key, get_db = kwargs.popitem()

    def deco(func: F) -> F:
        def wrapped(**kwargs):
            for db in get_db():
                return func(**{key: db, **kwargs})

        return wrapped

    return deco


@app.command(help="日時ジョブスケジューラを起動し、市場情報の更新とデイリートレードを行います。")
def start(immediate: bool =False):
    # import schedule  asyncが実装される予定だがまだ追加されていない
    from datetime import timedelta

    from magnet.etl import run_daily

    def get_tommorow():
        current = DateTimeAware.utcnow()
        tommorow = DateTimeAware(
            current.year, current.month, current.day, minute=10  # 最速で更新すると、変更が反映されていないことがあるので、時間を置く
        ) + timedelta(days=1)
        return tommorow

    async def exec_job():
        try:
            await run_daily()
        except Exception as e:
            print(e)

    async def main():
        while True:
            tommorow = get_tommorow()
            typer.echo(f"次回実行予定：{tommorow}　現在時刻：{DateTimeAware.utcnow()}")
            while True:
                current = DateTimeAware.utcnow()
                if current < tommorow:
                    await asyncio.sleep(60)
                    continue

                await exec_job()
                break

    if immediate:
        asyncio.run(exec_job())
    else:
        asyncio.run(main())


@app.command()
def run(
    id: int, *, mode: str = typer.Option("backtest", help="production|backtest|test")
):
    """トレードワーカーを起動します。"""

    jobs = get_account(id=id)
    if not jobs:
        return

    if len(jobs) > 1:
        raise Exception()

    job = jobs[0]

    from ...domain.trader2 import worker

    token = worker.get_cancel_token()
    loop = asyncio.get_event_loop()

    def ask_exit(signame):
        print(f"got signal: {signame}")
        token.is_canceled = True

    for signame in ("SIGINT", "SIGTERM"):
        loop.add_signal_handler(
            getattr(signal, signame), functools.partial(ask_exit, signame)
        )
    try:
        print(f"running worker for [{job.id} {job.name}]")
        loop.run_until_complete(worker.run(job, token, mode))
    except RuntimeError:
        # イベントループが途中で中断するとエラーが発生する
        # TODO: RuntimeErrorで他のRuntimeErrorを区別するには工夫が必要
        pass
    finally:
        loop.close()


@app.command(name="list")
def list_(
    user_id: int = typer.Option(..., help="ジョブid"),
    id: int = typer.Option(None, help="ジョブid"),
):
    id = undefined if id is None else id
    for item in get_account(user_id=user_id, id=id):
        print(f"{item.id} {item.name} {item.description}")


from ...domain.trader2.schemas import TradeAccount


@inject(db=get_db)
def get_account(db=None, *, user_id, id: int = undefined) -> List[TradeAccount]:
    from ...domain.trader2.views import TradeAccountService

    m = TradeAccountService.as_model()
    query = TradeAccountService.query(db).filter(m.user_id == user_id, m.id == id)

    return [TradeAccount.from_orm(x) for x in query]
