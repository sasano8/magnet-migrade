import datetime
from typing import List, Optional

from ...commons import BaseModel


class Dummy(BaseModel):
    class Config:
        orm_mode = True

    id: Optional[int] = None
    name: str
    date_naive: Optional[datetime.datetime] = None
    date_aware: Optional[datetime.datetime] = None
