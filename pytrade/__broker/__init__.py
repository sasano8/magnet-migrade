from decimal import Decimal

from .. import logic
from ..portfolio import VirtualAccount

# class Calculator:
#     def __init__(self, allocated_margin: Decimal):
#         self.margin = allocated_margin

#     def calc_amount_and_round_by_unit(self, real_price: Decimal, min_unit: Decimal):
#         return logic.calc_unit_amount(
#             budget=self.margin, real_price=real_price, min_unit=min_unit
#         )

#     def calc_amount_and_round_by_infered_min_unit(self, real_price: Decimal):
#         inferd = logic.infer_min_unit(real_price)
#         return logic.calc_unit_amount(
#             budget=self.margin, real_price=real_price, min_unit=inferd
#         )

#     @staticmethod
#     def infer_min_unit(price: Decimal) -> Decimal:
#         return logic.infer_min_unit(price)
