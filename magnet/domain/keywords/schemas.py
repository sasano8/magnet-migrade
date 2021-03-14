from typing import List, Optional

from ...commons import BaseModel


class Keywords(BaseModel):
    id: int
    category_name: str
    tag: str
    keywords: List[str] = []
    max_size: int = 1000
