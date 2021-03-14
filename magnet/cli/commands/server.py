import typer

app = typer.Typer()


LOGPATH = "/var/log/supervisor/fastapi-stdout.log"


@app.command()
def start(debug_vs_code: bool = False) -> None:
    """アプリケーションサーバを起動します"""
    import uvicorn

    from magnet import ENTRYPOINT_ASGI

    if not isinstance(ENTRYPOINT_ASGI, str):
        raise Exception("直接アプリケーションの参照を渡さないでください。プログラムが更新されても、リロードが反映されなくなります。")

    if not debug_vs_code:
        uvicorn.run(ENTRYPOINT_ASGI, host="0.0.0.0", port=8080)
    else:
        import debugpy

        # デバッガーがアタッチされるまで待機してからアプリケーションを起動する
        debugpy.listen(("0.0.0.0", 5678))
        debugpy.wait_for_client()

        uvicorn.run(
            ENTRYPOINT_ASGI,
            host="0.0.0.0",
            port=8080,
            reload=True,
            # reload_dirs=["magnet", "rabbitmq"],
        )


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
