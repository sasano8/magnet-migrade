from typing import List

from pandemic import APIRouter

from ...commons import PagenationQuery
from ...crawlers import google
from ...worker import queue_crawler

router = APIRouter()


@router.get("/")
async def index_crawler(q: PagenationQuery) -> List[str]:
    arr = list(queue_crawler.tasks)
    return arr


@router.post("/scrape_google")
def scrape_google(keyword: str):
    return google.scrape_google.delay(keyword=keyword)
