import typer

app = typer.Typer()


@app.command(help="メッセージの購読を開始します。")
def consume(reload: bool = False):
    queueing = get_queuing_instance()
    queueing.run()


def get_queuing_instance():
    import sys
    from importlib import import_module

    attr = "magnet.worker:queueing"
    module, attr = attr.split(":")

    # モジュールのリロード
    if module in sys.modules:
        sys.modules.pop(module)

    imported_module = import_module(module)
    instance = getattr(imported_module, attr)
    return instance
