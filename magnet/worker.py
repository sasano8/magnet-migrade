import asyncio
import logging

from framework.workers import SupervisorAsync
from rabbitmq import Rabbitmq

from .config import RabbitmqConfig

logger = logging.getLogger(__name__)
env = RabbitmqConfig()


rabbitmq_conn = Rabbitmq(url=env.RABBITMQ_HOST)  # 接続の確立と自動回復を試みる
queue_default = rabbitmq_conn.consumer(queue_name="default")
queue_crawler = rabbitmq_conn.consumer(queue_name="crawler", auto_ack=True)

queueing = SupervisorAsync([rabbitmq_conn, queue_default, queue_crawler]).to_executor(
    logger=logger
)


async def start_consume():
    """メッセージキューの購読を開始します。"""
    queueing.start()


async def stop_consume():
    """メッセージキューの購読を終了します。"""
    await queueing.stop()


from .database import get_db

workers = SupervisorAsync().to_executor(logger=logger)


@queue_default.task
async def func():
    print("hello 1 !!!!")
    await asyncio.sleep(1)
    func.delay()
