from typing import List, Optional

from ...commons import BaseModel


class CaseNode(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str


class Target(BaseModel):
    class Config:
        orm_mode = True

    id: int
    name: str
    node_id: int
