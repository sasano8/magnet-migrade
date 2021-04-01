from typer import Typer


def setup(func):
    func()
    return func


app = Typer()


@setup
def build_commands():
    from magnet.cli.commands import config, db, queue, server, tests, trade

    app.add_typer(server.app, name="server", help="APIサーバー関連のコマンド集です。")
    app.add_typer(config.app, name="config", help="設定ファイル関連のコマンド集です。")
    app.add_typer(db.app, name="db", help="データベース関連のコマンド集です。")
    app.add_typer(tests.app, name="tests", help="テスト関連のコマンド集です。")
    app.add_typer(trade.app, name="trade", help="トレード関連のコマンド集です。")
    app.add_typer(queue.app, name="queue", help="メッセージキューによる非同期処理ワーカーに関連するコマンド集です。")
