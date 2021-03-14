from magnet.ingester.schemas import TaskCreate, CommonSchema
from . import crawlers

@crawlers
def scrape_dummy(driver, input: CommonSchema):

    for i in [1, 2]:
        item = input.copy_summary()
        item.detail.no = i

        yield item

