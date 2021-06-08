import asyncio
import logging

import asy
from asy_rabbitmq import Rabbitmq

from .config import RabbitmqConfig

logger = logging.getLogger(__name__)
env = RabbitmqConfig()


rabbitmq = Rabbitmq(host=env.RABBITMQ_HOST)
queue_default = rabbitmq.consumer(queue_name="default", auto_ack=False)
queue_extract = rabbitmq.consumer(queue_name="extract", auto_ack=True)
queue_transform = rabbitmq.consumer(queue_name="transform", auto_ack=True)
# queue_load = rabbitmq.consumer(queue_name="transform", auto_ack=True)

queueing = asy.supervise(queue_default, queue_extract, queue_transform)
