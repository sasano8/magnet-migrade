from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .portfolio import TradePosition as P


class TradePositionProperty:
    @property
    def is_entry_order(self: "P"):
        return self.entry_id is None
