import asyncio
import logging

import asy
from asy_rabbitmq import RabbitmqParam

from .config import RabbitmqConfig

logger = logging.getLogger(__name__)
env = RabbitmqConfig()


rabbitmq = RabbitmqParam(host=env.RABBITMQ_HOST)
queue_default = rabbitmq.consumer(queue_name="default")
queue_crawler = rabbitmq.consumer(queue_name="crawler", auto_ack=True)


queueing = asy.supervise(queue_default, queue_crawler)


from .database import get_db

workers = asy.supervise()


@queue_default.task
async def func():
    print("hello 1 !!!!")
    await asyncio.sleep(1)
    func.delay()


def setup_worker():
    asy.supervise(
        "ラビットMQの親コネクションの確立と再接続を行う",
        "クローラーキューを購読してクローラを実行する",
        "市場を監視してトレードシグナルを流す（１５分ごと）",
        "市場を監視してトレードシグナルを流す（１日ごと）",
        "前日のOHLCを最新化して分析する（１日ごと）",
        "トレードシグナルキューを購読してトレードを行う",
        "トレード注文を監視して、完了したトレードを記録する",
    )
