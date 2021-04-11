"""
get_driver_managerにより、シングルトンのセレニウムインスタンスを取得する。
クローラの並列起動をしたい場合は、ワーカーを多重起動する。（未検証）
"""

import logging
import os

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

logger = logging.getLogger(__name__)


def create_driver():
    connector = ""
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("--blink-settings=imagesEnabled=false")

    is_debug = bool(os.environ.get("IS_SELENIUM_DEBUG", False))
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


def get_driver():
    try:
        driver = create_driver()
        yield driver
    finally:
        driver.quit()


def cleanup_driver(self):
    """
    インスタンスを使い回す場合は以下のように実装する
    """
    driver = self.driver

    for handle in driver.window_handles:
        driver.switch_to.window(handle)
        if len(driver.window_handles) != 1:
            driver.close()

    driver.get("about:blank")
    logger.info("browser was cleaned up.")
