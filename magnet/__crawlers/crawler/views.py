from typing import List, Optional
from . import crud
from magnet import get_db, TemplateView, PagenationQuery
from magnet.vendors import cbv, InferringRouter, fastapi_funnel


router = InferringRouter()

@cbv(router)
class CrawlerView(TemplateView[crud.crawlers]):
    @property
    def rep(self) -> crud.crawlers:
        raise NotImplementedError()

    @router.get("/")
    @fastapi_funnel
    async def index(self, q: PagenationQuery) -> List[str]:
        mapping = map(lambda key_value: key_value[0], crud.crawlers.list())
        arr = list(mapping)
        return arr
