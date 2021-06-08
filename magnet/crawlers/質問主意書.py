import asyncio
from urllib.parse import urljoin

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def exec_large_volume_holding():
    """質問主意書を収集する"""
    url = "https://www.sangiin.go.jp/japanese/joho1/kousei/syuisyo/201/syuisyo.htm"


import logging

import httpx
from bs4 import BeautifulSoup
from fastapi import Depends

from magnet.worker import queue_extract, queue_transform

from ..driver import WebDriver, get_driver

logger = logging.getLogger(__name__)


@queue_extract.task
async def get_all_content_govement_question():
    page_max = "204"
    url = "https://www.sangiin.go.jp/japanese/joho1/kousei/syuisyo/{page}/syuisyo.htm"

    async with httpx.AsyncClient() as client:
        content = await client.get(url.format(page=page_max))

    soup = BeautifulSoup(content, "html.parser")
    pages = soup.select("select[title='国会回次指定'] > option")
    page_numbers = [x["value"].split("/")[5] for x in pages]
    page_numbers = sorted(page_numbers, reverse=True)

    for no in page_numbers:
        await asyncio.sleep(3)
        page_url = url.format(page=no)
        async with httpx.AsyncClient() as client:
            page_content = await client.get(page_url)

        result = {"no": int(no), "url": page_url, "content": page_content.text}
        get_content_govement_question.delay(**result)


@queue_transform.task
async def get_content_govement_question(no, url: str, content):
    soup = BeautifulSoup(content, "html.parser")
    table = soup.select_one("#ContentsBox > .list_c")
    rows = list(table.select("tr"))
    row_count = len(rows)
    current_row = 0

    content_row = 0

    while current_row < row_count:
        el = rows[current_row]
        if el.select("th")[0].text != "提出番号":
            raise Exception()

        try:
            title = el.select_one("td > a").text
            link = el.select_one("td > a")["href"]

            current_row += 1
            el = rows[current_row]
            提出者 = el.select_one("td.ta_l").text
            links = el.select("td > a")
            質問本文 = links[0]["href"]
            答弁本文 = links[1]["href"]

            current_row += 2
            content_row += 1
        except:
            raise

        result = {
            "row": content_row,
            "title": title,
            "提出者": 提出者,
            "link_title": urljoin(url, link),
            "link_質問本文": urljoin(url, 質問本文),
            "link_答弁本文": urljoin(url, 答弁本文),
        }

        logger.info(result)
