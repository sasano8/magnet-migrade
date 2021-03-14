"""
get_driver_managerにより、シングルトンのセレニウムインスタンスを取得する。
クローラの並列起動をしたい場合は、ワーカーを多重起動する。（未検証）
"""

import os

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities

from magnet import logger


class SeleniumManager:
    def __init__(self):
        self.driver = None
        self.init()

    def init(self):
        self.driver = self.create_driver()

        # プロセス終了時にブラウザを終了させる
        import signal

        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def handle_exit(self, sig, frame):
        self.__del__()

    def is_active(self):
        if self.driver:
            return True
        else:
            return False

    def create_driver(self):
        if self.driver:
            raise Exception("Driver is already created.")

        else:
            # from selenium import webdriver
            # from selenium.webdriver import DesiredCapabilities

            logger.info("create driver.")
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

    def cleanup_driver(self):
        """
        ブラウザタブを１つにし、ブランクページを開く。
        これは、ブラウザ起動コスト削減するため、インスタンスを再利用するため。
        """
        driver = self.driver

        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            if len(driver.window_handles) != 1:
                driver.close()

        driver.get("about:blank")
        logger.info("browser was cleaned up.")

    def quit(self):
        self.__del__()

    def __del__(self):
        if not self.driver:
            return

        self.driver.quit()
        self.driver = None


__DRIVER = None


def get_driver_manager():
    global __DRIVER

    if __DRIVER:
        return __DRIVER

    __DRIVER = SeleniumManager()
    return __DRIVER
