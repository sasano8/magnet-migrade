from pydantic import BaseModel

# 注文は常に成行で行う
# キャンセルは考慮しない


class VirtualAccountEntryOrder(BaseModel):
    pass


class VirtualAccountEntryOrderFetch(BaseModel):
    pass


class VirtualAccountEntryOrderContracted(BaseModel):
    pass


# class VirtualAccountEntryOrderNoContracted(BaseModel):
#     pass


class VirtualAccountCloseOrder(BaseModel):
    pass


class VirtualAccountCloseOrderFetch(BaseModel):
    pass


class VirtualAccountCloseOrderContracted(BaseModel):
    pass


# class VirtualAccountCloseOrderNoContracted(BaseModel):
#     pass
