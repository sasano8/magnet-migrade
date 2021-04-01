import logging

from fastapi.middleware.gzip import GZipMiddleware

# from magnet.core import middlewares
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

import pandemic

from . import errors
from .worker import workers

logger = logging.getLogger(__name__)

# TODO: swagger ui configがサポートされたら、persistAuthorizationでリロード時に認証がキープされるか確認する
# https://github.com/tiangolo/fastapi/pull/2568
# app = pandemic.FastAPI(swagger_ui_parameters={"persistAuthorization": True})
app = pandemic.FastAPI()


def setup(func):
    func()
    return func


@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
    <head>
        <title>hello my application.</title>
    </head>
    <body>
        <a href="docs">docs</a><br>
        <a href="redoc">redoc</a><br>
        <a href="http://localhost:8888">jupyter</a><br>
        <a href="http://localhost:8501">streamlit</a><br>
        <a href="http://localhost:5050">pgadmin</a><br>
        <code>
        sudo jupyter contrib nbextension install<br>
        sudo jupyter nbextensions_configurator enable<br>
        sudoをつけないとファイルの更新に失敗する。matplotlibを実行できない
        sudo jupyter notebook --ip=0.0.0.0 --allow-root --notebook-dir=jupyter --NotebookApp.token='' --NotebookApp.password='' &<br>
        streamlit run magnet/streamlit_ui/main.py<br>
        </code>
    </body>
    </html>
    """


@setup
def add_routers():
    import magnet.domain.crawlers.views
    import magnet.domain.develop.views
    import magnet.domain.scaffold.views
    import magnet.domain.system.views
    import magnet.domain.trade.views

    # import magnet.domain.trader.views
    import magnet.domain.user.views

    # configration router
    app.include_router(magnet.domain.user.views.guest_router, prefix="/guest")
    app.include_router(magnet.domain.user.views.user_me_router, prefix="/me")
    app.include_router(magnet.domain.user.views.user_router, prefix="/users")
    # app.include_router(magnet.domain.trader.views.router, prefix="/trader")
    app.include_router(magnet.domain.trade.views.router, prefix="/bot")
    # app.include_router(magnet.crawler.views.router, prefix="/crawler")
    # app.include_router(magnet.executor.views.router, prefix="/executor")
    # app.include_router(magnet.ingester.views.router, prefix="/ingester")
    # app.include_router(magnet.trader.views.router, prefix="/trader")
    app.include_router(magnet.domain.crawlers.views.router, prefix="/crawlers")
    app.include_router(magnet.domain.scaffold.views.router, prefix="/scaffold")
    app.include_router(magnet.domain.develop.views.router, prefix="/develop")
    app.include_router(magnet.domain.system.views.router, prefix="/system")


@setup
def add_middlewares():
    # configration middlewares
    # ミドルウェアの実行順序は、最後に追加したミドルウェアから実行されていく
    # app.add_middleware(magnet.message.middlewares.ExceptionMiddleware)
    # app.add_middleware(middlewares.CorsMiddleware) # 未実装
    app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(errors.AppException)
async def exc_app(request, exc):
    return errors.handle_error(request, exc)


from .worker import func


@app.on_event("startup")
async def startup_worker():
    """ワーカーを起動します"""

    # from .domain.order import Broker

    # client = Broker("bitflyer")
    # await client()
    workers.start()


@app.on_event("shutdown")
async def shutdown_worker():
    """ワーカーを終了します"""
    await workers.stop()
    # await supervisor.stop()


# from . import notify

# notify.broadcast("へいへいへい！")


# 取引アルゴリズム　やること

# TESLAはビットコインと連動する
