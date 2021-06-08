import typer

app = typer.Typer()


LOGPATH = "/var/log/supervisor/fastapi-stdout.log"


@app.command()
def start(
    host: str = "0.0.0.0",
    port: int = 8080,
    reload: bool = False,
) -> None:
    """アプリケーションサーバを起動します"""
    import uvicorn

    from magnet import ENTRYPOINT_ASGI
    from magnet.config import ModeConfigCreate

    if ModeConfigCreate().MODE == "DEBUG":
        """
        supervisorによりサーバーが自動起動するが、DEBUG時はサーバーを直接起動せず、IDE等からプロセスを起動することを想定する。
        サーバーが二重起動すると、メッセージキュー処理が勝手に並列になったり、面倒事が生じるため
        """
        return

    if not isinstance(ENTRYPOINT_ASGI, str):
        raise Exception("直接アプリケーションの参照を渡さないでください。プログラムが更新されても、リロードが反映されなくなります。")

    # lifespan=on: startup shutdownイベント時に例外を捕捉する
    uvicorn.run(ENTRYPOINT_ASGI, host=host, port=port, reload=reload, lifespan="on")


@app.command()
def events() -> None:
    """アプリケーションのイベント一覧を取得します"""
    from magnet.__main import app

    events = {
        "startup": [
            f"{event.__module__}.{event.__name__} {event.__doc__}"
            for event in app.router.on_startup
        ],
        "shutdown": [
            f"{event.__module__}.{event.__name__} {event.__doc__}"
            for event in app.router.on_shutdown
        ],
    }
    typer.echo(events)


@app.command()
def workers() -> None:
    """アプリケーションに関するワーカー一覧を取得します"""


@app.command()
def log() -> None:
    import subprocess

    args = ["less", "+F", LOGPATH]
    subprocess.check_call(args)


@app.command()
def show_log_path():
    typer.echo(LOGPATH)
