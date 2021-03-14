ENTRYPOINT_ASGI = "magnet.__main:app"


def setup(func):
    func()
    return func


@setup
def check_platform():
    """前提環境の検証を行う"""
    import locale

    from tzlocal import get_localzone

    system_locale = locale.getdefaultlocale()
    language_code = system_locale[0]
    encoding = system_locale[1]
    local_tz = get_localzone()

    if not language_code == "en_US":
        raise Exception(f"Not allowed language_code: {language_code}")

    if not encoding == "UTF-8":
        raise Exception(f"Not allowed encoding: {encoding}")

    if not str(local_tz) == "UTC":
        raise Exception(f"Not allowed timezone: {local_tz}")


@setup
def setup_logging_basic_config():
    """環境変数に応じてログ設定を変更する。"""
    import logging

    from fastapi.logger import logger

    from .config import LogConfig

    log_setting = LogConfig()

    logging.basicConfig(
        level=logging._nameToLevel[log_setting.log_level],
        datefmt=log_setting.log_format_date,
        format=log_setting.log_format_msg,
    )

    # supervisor経由でログが上手く表示されない対応
    gunicorn_logger = logging.getLogger("gunicorn.error")
    logger.handlers = gunicorn_logger.handlers
    if __name__ == "main":
        logger.setLevel(logging.DEBUG)
        logger.debug("bbbbbbbbb")
    else:
        logger.debug("aaaaaaaa")
        logger.setLevel(gunicorn_logger.level)


@setup
def setup_database_module():
    """データベースに関連するモジュールを読み込む。"""
    import os

    from . import database
    from .utils import importer

    cd = os.path.dirname(__file__) + "/domain"
    if not os.path.exists(cd):
        raise FileNotFoundError(cd)
    importer.import_modules(cd, ["models.py"])


@setup
def setup_event_module():
    """アプリケーションイベントを登録する。"""
    import os

    from .utils import importer

    cd = os.path.dirname(__file__) + "/domain"
    if not os.path.exists(cd):
        raise FileNotFoundError(cd)
    importer.import_modules(cd, ["events.py"])


@setup
def setup_crawler_module():
    """クローラーに関連するモジュールを読み込む。"""
    from .crawlers import google


@setup
def setup_worker_module():
    ...
    """ワーカーを管理するスーパーバイザーを初期化する。"""
    from . import worker
