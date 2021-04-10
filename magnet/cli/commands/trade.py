import asyncio
import logging
import traceback
from typing import Callable, List, TypeVar

import typer

from framework import DateTimeAware

F = TypeVar("F", bound=Callable)

app = typer.Typer()

logger = logging.getLogger(__name__)




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
            logger.critical(traceback.format_exc())

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

