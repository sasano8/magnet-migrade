import asyncio
import logging

from framework.workers import SupervisorAsync
from rabbitmq import Rabbitmq

from .config import RabbitmqConfig

logger = logging.getLogger(__name__)
env = RabbitmqConfig()

# ===================================================
# rabbitmq workers
# ===================================================
# TODO: ラウンドロビンに対応させたい
rabbitmq_conn = Rabbitmq(url=env.RABBITMQ_HOST)  # 接続の確立と自動回復を試みる
queue_default = rabbitmq_conn.consumer(
    queue_name="default"
)  # 接続上にチャンネルを作成し、キューからメッセージ受信
queue_crawler = rabbitmq_conn.consumer(queue_name="crawler", auto_ack=True)


# ===================================================
# brokers
# ===================================================
from .domain.broker.worker import BitflyerBroker

broker = BitflyerBroker()

# workers = SupervisorAsync(
#     [rabbitmq_conn, queue_default, queue_crawler, broker]
# ).to_executor(logger=logger)

workers = SupervisorAsync([broker]).to_executor(logger=logger)


@queue_default.task
async def func():
    print("hello 1 !!!!")
    await asyncio.sleep(1)
    func.delay()
