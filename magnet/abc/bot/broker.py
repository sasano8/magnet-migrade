"""
ブローカーbotと取引所間の売買取引を仲介する。
本モジュールにおけるブローカーの責務は以下の通り。

1. 注文の管理
2. 発注
3. 注文の監視・更新

注文が更新はトリガーされ、更新時にコールバックイベントが発火する。
ブローカーは、各取引所毎に実装する必要がある。
"""

from abc import ABC, abstractclassmethod


class Order:
    pass


class Broker(ABC):
    def __init__(self) -> None:
        pass

    async def observe(self):
        pass

    @abstractclassmethod
    async def fetch(self, order) -> Order:
        pass
