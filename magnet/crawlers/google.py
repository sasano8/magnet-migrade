import asyncio
import logging
import time
from typing import Any, List, Optional

from fastapi import Depends
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from magnet.worker import queue_crawler

from ..commons import BaseModel
from ..driver import get_driver

logger = logging.getLogger("google")


class Detail(BaseModel):
    url: Optional[str]
    url_cache: Optional[str]
    title: Optional[str]
    summary: Optional[str]

    class Config:
        extra = "allow"


# from magnet.ingester.schemas import CommonSchema, TaskCreate
class TaskCreate(BaseModel):
    pipeline_name: str = "postgress"
    crawler_name: str
    keyword: str
    option_keywords: List[Any] = []
    deps: int = 0

    # openapi上でデフォルト値は認識されないため、サンプルを明示的に定義する
    class Config:
        schema_extra = {
            "example": {
                "pipeline_name": "postgres",
                "crawler_name": "scrape_google",
                "keyword": "山田太郎",
            }
        }


class CommonSchema(TaskCreate):
    # Config = ORM
    class Config:
        orm_mode = True

    # pipeline: str
    # crawler_name: str
    # keyword: str
    # option_keywords: List[str] = []
    # deps: int = 0
    referer: Optional[str]
    url: Optional[str]
    url_cache: Optional[str]
    title: Optional[str]
    summary: Optional[str]
    current_page_num: int = 0
    detail: Detail = Detail()

    def copy_summary(self):
        dic = self.dict(exclude={"detail"})
        obj = self.__class__.construct(**dic)
        return obj

    def sync_summary_from_detail(self):
        self.url = self.detail.url
        self.url_cache = self.detail.url_cache
        self.title = self.detail.title
        self.summary = self.detail.summary


@queue_crawler.task
async def scrape_google(driver=Depends(get_driver), *, keyword: str):
    # TODO: optionを追加する
    state = CommonSchema(crawler_name="google", keyword=keyword)  # 引数で受け入れること
    # state = input

    # condition = '({0})'.format(' OR '.join(state.option_keywords))
    if len(state.option_keywords):
        search_keyword = state.keyword + " (" + " OR ".join(state.option_keywords) + ")"
    else:
        search_keyword = state.keyword

    # search_keyword = state.keyword + ' ' + condition
    state.referer = "https://www.google.com/search?query={0}&hl=ja&num={1}".format(
        search_keyword, 100
    )
    driver.get(state.referer)

    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)

    # TODO: 0件の時のチェック
    # TODO: booksの検索結果が取得できていない
    # 再現URL:https://www.google.com/search?query=%E5%B1%B1%E7%94%B0%E5%A4%AA%E9%83%8E%20(%E5%8D%98%E8%AA%9E%20OR%20%E5%8F%B3%E7%BF%BC%20OR%20%E6%A8%AA%E9%A0%98%20OR%20%E8%AA%B2%E7%A8%8E%20OR%20%E8%A7%A3%E4%BB%BB%20OR%20%E6%94%B9%E5%96%84%E5%91%BD%E4%BB%A4%20OR%20%E5%8B%A7%E5%91%8A%20OR%20%E8%B5%B7%E8%A8%B4%20OR%20%E6%A5%AD%E5%8B%99%E5%81%9C%E6%AD%A2%20OR%20%E5%91%8A%E8%A8%B4%20OR%20%E5%B7%A6%E7%BF%BC%20OR%20%E8%A9%90%E6%AC%BA%20OR%20%E4%BB%95%E6%89%8B%20OR%20%E9%8A%83%20OR%20%E8%A8%B4%E8%A8%9F%20OR%20%E9%80%81%E6%A4%9C%20OR%20%E9%80%AE%E6%8D%95%20OR%20%E8%84%B1%E7%A8%8E%20OR%20%E5%BC%BE%E4%B8%B8%20OR%20%E5%BC%BE%E7%97%95%20OR%20%E8%BF%BD%E5%BE%B4%20OR%20%E6%8F%90%E8%A8%B4%20OR%20%E5%80%92%E7%94%A3%20OR%20%E5%90%8C%E5%92%8C%20OR%20%E7%A0%B4%E7%94%A3%20OR%20%E8%83%8C%E4%BB%BB%20OR%20%E7%99%BA%E7%A0%B2%20OR%20%E5%8F%8D%E5%B8%82%E5%A0%B4%20OR%20%E5%8F%8D%E7%A4%BE%E4%BC%9A%20OR%20%E6%9A%B4%E5%8A%9B%E5%9B%A3%20OR%20%E6%B0%91%E4%BA%8B%E5%86%8D%E7%94%9F%20OR%20%E5%AE%B9%E7%96%91%20OR%20%E6%BC%8F%E3%81%88%E3%81%84%20OR%20%E6%BC%8F%E6%B4%A9)&hl=ja&num=100

    while True:

        await asyncio.sleep(3)

        # googleが勝手に予測し、検索キーワードを変えることがある
        # その場合は、元の検索キーワードという通知領域が存在する　再現例：「グロープワープ」で検索
        if len(driver.find_elements_by_css_selector("#taw #fprs")) > 0:
            original_keyword = driver.find_elements_by_css_selector(
                "#taw #fprs A.spell_orig"
            )[0]
            original_keyword.click()

        # captchaに対して無理やり処理を行うと使用拒否の可能性もあるので無理をしない
        # その際は、人の手で何とか対応させたい
        if len(driver.find_elements_by_css_selector("#captcha-form")) > 0:
            logging.warning("detected captcha.")
            time.sleep(100)

        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)

        # 検索結果画面
        state.current_page_num += 1

        # list_div = driver.find_elements_by_css_selector("#search div.rc")
        # .eejeod - SNSなどが表示されており構造が違うから除外
        list_div = driver.find_elements_by_css_selector("#search div.g:not(.eejeod)")

        if len(list_div) == 0:
            raise Exception("Not Found Selector -> #search div.g")

        i = 0

        for el in list_div:
            await asyncio.sleep(0)

            i += 1
            logger.debug(i)

            # stateからtargetとかを自動で設定する
            # Metaからsource_groupとかを設定する
            # item = self.item_model.create_and_relation_query(state, **self.get_meta_dic())
            item = state.copy_summary()
            detail = item.detail
            # detail.url = el.find_elements_by_css_selector(".r > a")[0].get_attribute(
            #     "href"
            # )
            # detail.title = el.find_elements_by_css_selector(".r > a > h3")[0].text
            # detail.summary = el.find_elements_by_css_selector(".s > DIV > SPAN")[0].text

            detail.url = el.find_elements_by_css_selector(".yuRUbf > a")[
                0
            ].get_attribute("href")
            detail.title = el.find_elements_by_css_selector(".yuRUbf > a > h3")[0].text
            detail.summary = el.find_elements_by_css_selector("SPAN.aCOpRe > SPAN")[
                0
            ].text

            # detail = {}
            # item.detail = {
            #     self.crawler_name: detail
            # }
            # item.detail.url = item.url
            # item.detail.title = item.title
            # item.detail.summary = item.summary

            # detail['url'] = item.url
            # detail['title'] = item.title
            # detail['summary'] = item.summary

            # キャッシュがあればurlを取得しておく
            # 2021/2 キャッシュは消滅した模様？
            # elements = el.find_elements_by_css_selector(".action-menu-item > A")
            # if len(elements) > 0:
            #     detail.url_cache = elements[0].get_attribute("href")

            # yield item
            logger.info(item)

        # 次のページがあれば次のページへ
        try:
            next_page = driver.find_elements_by_css_selector("#pnnext")[0]

        except:
            break

        next_page.click()
