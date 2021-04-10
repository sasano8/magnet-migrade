import asyncio
import logging

import asy

from rabbitmq import Rabbitmq

from .config import RabbitmqConfig

logger = logging.getLogger(__name__)
env = RabbitmqConfig()


rabbitmq_conn = Rabbitmq(url=env.RABBITMQ_HOST)  # 接続の確立と自動回復を試みる
queue_default = rabbitmq_conn.consumer(queue_name="default")
queue_crawler = rabbitmq_conn.consumer(queue_name="crawler", auto_ack=True)

queueing = asy.supervise(rabbitmq_conn, queue_default, queue_crawler)


async def start_consume():
    """メッセージキューの購読を開始します。"""
    queueing.start()


async def stop_consume():
    """メッセージキューの購読を終了します。"""
    await queueing.stop()


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
