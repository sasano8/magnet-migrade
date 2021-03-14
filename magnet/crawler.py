# ドライバープール
# クローラ関数への参照クラス
# クローラ一覧ビュー

import logging
from dataclasses import dataclass, field
from typing import Callable, Coroutine, Dict, List, TypeVar

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from framework.analyzers import FuncAnalyzer

from .commons import BaseModel
from .worker import queue_crawler

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable)


def create_driver(is_debug: bool = False) -> webdriver.Remote:

    logger.info("create driver.")
    connector = ""
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("--blink-settings=imagesEnabled=false")

    # is_debug = bool(os.environ.get("IS_SELENIUM_DEBUG", False))
    is_debug = True

    if is_debug:
        connector = "http://localhost:4444/wd/hub"
    else:
        connector = "http://selenium:4444/wd/hub"

    driver = webdriver.Remote(
        command_executor=connector,
        desired_capabilities=DesiredCapabilities.CHROME.copy(),
        options=chrome_option,
        keep_alive=True,
    )

    return driver


def cleanup_driver(driver: webdriver.Remote):
    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if len(driver.window_handles) != 1:
            driver.close()

    driver.get("about:blank")
    logger.info("browser was cleaned up.")


@dataclass
class DriverPool:
    def __post_init__(self):
        self.drivers: List[webdriver.Remote] = []

    def create_instance(self):
        driver = create_driver()
        self.drivers.append(driver)

    def get_driver(self):
        if len(self.drivers) == 0:
            self.create_instance()

        return self.drivers[0]

    def __del__(self):
        for driver in self.drivers:
            try:
                driver.quit()
            except Exception as e:
                pass


@dataclass
class CrawlerManager:
    def __post_init__(self):
        self.depends_on(DriverPool())
        self.funcs: Dict[str, Callable[..., Coroutine]] = {}

    def depends_on(self, driver_pool: DriverPool):
        self.driver_pool = driver_pool

    def task(self, func: F) -> F:
        obj = FuncAnalyzer(func)
        if not obj.is_callable():
            raise TypeError(f"{func} is not callable.")
        if obj.is_asyncgenerator_callable():
            raise TypeError(f"{func} is not callable. type: async generator")
        if obj.is_generator_callable():
            raise TypeError(f"{func} is not callable. type: generator")
        new_func = obj.to_coroutine_callable()
        self.funcs[new_func.__name__] = new_func
        return func

    def option(self, domain: str = "", retry: int = 0):
        pass

    async def request(self, func_name, /, *args, **kwargs):
        func = self.funcs[func_name]
        driver = self.driver_pool.get_driver()
        try:
            await func(driver, *args, **kwargs)
        except Exception as e:
            logger.critical(str(e))
        cleanup_driver(driver)


class RequestCrawler(BaseModel):
    func_name: str
    args: list
    kwargs: dict


crawlers = CrawlerManager()


@queue_crawler.task
async def request_crawler(func_name, /, *args, **kwargs):
    await crawlers.request(func_name, *args, **kwargs)


from .crawlers import google
