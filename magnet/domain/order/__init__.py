# from decimal import Decimal
# from typing import Any, Literal

# from pydantic import BaseModel, Field, root_validator

# from framework import DateTimeAware

# from ...commons import intellisense


def init():
    from . import models  # isort:skip
    from . import brokers  # isort:skip
    from . import topics  # isort:skip
    from . import analyzers  # isort:skip


init()

# @intellisense
# class Order(BaseModel):
#     currency_pair: str
#     bid_or_ask: Literal["ask", "bid"]
#     order_type: Literal["market", "limit"] = "market"
#     time_in_force: Literal["GTC", "IOC", "FOK"] = Field("GTC", const=True)
#     order_date: DateTimeAware = None
#     result_info: dict = None
#     price: Decimal = None
#     amount: Decimal = 0
#     limit: Decimal = None
#     loss: Decimal = None
#     comment: str = None
#     reason: str = ""
#     sys_comment: str = "テスト中"

#     @property
#     def is_done(self) -> bool:
#         return self._is_done(self.order_date, self.result_info)

#     @classmethod
#     def _is_done(cls, order_date, result_info):
#         if order_date is None and result_info is None:
#             result = False
#         elif order_date is not None and result_info is not None:
#             result = True
#         else:
#             raise ValueError()
#         return result

#     @root_validator()
#     def valid_status(cls, values):
#         order_date = values.get("order_date", None)
#         result_info = values.get("result_info", None)
#         cls._is_done(order_date, result_info)
#         return values

#     def get_invert_bid_or_ask(self) -> str:
#         if self.bid_or_ask == "ask":
#             return "bid"
#         elif self.bid_or_ask == "bid":
#             return "ask"
#         else:
#             raise Exception()


# from enum import Enum


# class BuyAsk(str, Enum):
#     BUY = "BUY"
#     SELL = "SELL"
