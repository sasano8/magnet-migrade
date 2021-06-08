from typing import List

from pandemic import APIRouter

from ...commons import PagenationQuery
from ...crawlers import google, 質問主意書
from ...worker import queue_extract

router = APIRouter()


@router.get("/")
async def index_crawler(q: PagenationQuery) -> List[str]:
    arr = list(queue_extract.tasks)
    return arr


@router.post("/scrape_google")
def scrape_google(keyword: str):
    return google.scrape_google.delay(keyword=keyword)


@router.post("/scrape_all_govement_question")
def scrape_all_govement_question():
    return 質問主意書.get_all_content_govement_question.delay()
