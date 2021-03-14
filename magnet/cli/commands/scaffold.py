import typer

from magnet.cli.errors import handle_error
from magnet.config import DatabaseConfigCreate

app = typer.Typer()


@app.command()
# unpack.typer
@handle_error
def sample(input: DatabaseConfigCreate) -> None:
    """アプリケーション起動に必要な設定ファイル（.env）を生成します。"""

    typer.echo(DatabaseConfigCreate)
