import os
from functools import partial

import typer

from magnet.cli.errors import handle_error
from magnet.config import AllConfigCreate, DatabaseConfig, DatabaseConfigCreate
from pandemic import Adapters, SignatureBuilder

app = typer.Typer()

to_typer = SignatureBuilder.unpack_arguments(Adapters.to_typer, prompt=True)


@app.command()
@to_typer
@handle_error
def init(input: AllConfigCreate) -> None:
    """アプリケーション起動に必要な設定ファイル（.env）を生成します。"""

    path = ".env"
    if os.path.exists(path):
        raise FileExistsError(".envファイルがすでに存在します。")

    with open(path, mode="x") as f:
        f.write(input.to_env_file_str())

    typer.echo(f"Generated {path}")
    typer.echo(f"Please reopen container.")


@app.command()
@handle_error
def show() -> None:
    """設定の検証と表示を行います。"""

    obj = DatabaseConfig()
    typer.echo(obj.to_env_file_str())
