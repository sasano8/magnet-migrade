import asyncio
import logging

import asy
from asy_rabbitmq import Rabbitmq

from .config import RabbitmqConfig

logger = logging.getLogger(__name__)
env = RabbitmqConfig()


rabbitmq = Rabbitmq(host=env.RABBITMQ_HOST)
queue_default = rabbitmq.consumer(queue_name="default")
queue_crawler = rabbitmq.consumer(queue_name="crawler", auto_ack=True)


queueing = asy.supervise(queue_default, queue_crawler)
