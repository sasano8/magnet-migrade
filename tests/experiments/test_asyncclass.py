import asyncio
from asyncio import tasks

from pydantic import BaseModel, Field


class Sample:
    async def __call__(self):
        await asyncio.sleep(5)
        return 1


class Broker(BaseModel):
    broker_url: str
    queue_name: str = "default"
    tasks: dict = {}
    durable: bool = True
    auto_ack: bool = Field(False, description="メッセージ受信時に応答を返す。応答を返すとメッセージはキューから削除される。")
    inactivity_timeout: int = 1
    timeout_when_connection_close: int = 10


class AsyncWorker:
    def __init__(self) -> None:
        pass

    async def __call__(self):
        return self.start

    async def start(self):
        return self.wait_queue


def test_async():
    obj = Sample()

    result = asyncio.run(obj())
    assert result == 1
