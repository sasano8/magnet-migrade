import asyncio
import logging
from typing import Callable

from pydantic import BaseModel

logger = logging.getLogger("rabbitmq")
logger.setLevel("INFO")


# TODO: rabbitmqのワーカーをこれに差し替える
# TODO: awasome async framework https://github.com/b2wdigital/async-worker
class AsyncWorker(BaseModel):
    func: Callable
    __is_stoped: bool = True

    def startup(self):
        logger.info("consumer initializing...")
        self.install_signal_handlers()

    def install_signal_handlers(self):
        import signal

        HANDLED_SIGNALS = (
            signal.SIGINT,  # Unix signal 2. Sent by Ctrl+C.
            signal.SIGTERM,  # Unix signal 15. Sent by `kill <pid>`.
        )

        # TODO: modify get_running_loop
        loop = asyncio.get_event_loop()

        try:
            for sig in HANDLED_SIGNALS:
                # メインスレッドで呼び出さなければいけない。
                # メインスレッド
                loop.add_signal_handler(sig, self.handle_exit, sig, None)
        except NotImplementedError:
            # for Windows
            for sig in HANDLED_SIGNALS:
                signal.signal(sig, self.handle_exit)

    def handle_exit(self, sig, frame):
        self.stop()

    def stop(self):
        self.__is_stoped = True

    @property
    def is_stoped(self):
        return self.__is_stoped

    async def run(self):
        self.startup()
        self.__is_stoped = False

        while True:
            if self.__is_stoped:
                break

            await self.func()
