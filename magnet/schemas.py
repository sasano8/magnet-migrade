from typing import Any, List

from pydantic import BaseModel


class Exception(BaseModel):
    pass


# commonに移して削除する
class BulkResult(BaseModel):
    deleted: int
    inserted: int
    errors: List[Any]


class Page(BaseModel):
    pass
