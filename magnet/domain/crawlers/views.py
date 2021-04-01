from typing import List

from pandemic import APIRouter

from ...commons import PagenationQuery
from . import crud

router = APIRouter()


@router.get("/")
async def index_crawler(q: PagenationQuery) -> List[str]:
    mapping = map(lambda key_value: key_value[0], crud.crawlers.list())
    arr = list(mapping)
    return arr


for key, func in crud.crawlers.list():
    router.get("/" + key)(func)
