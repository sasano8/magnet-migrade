import inspect
from typing import Literal, Optional

import pytest
import typer
from pydantic import BaseModel
from typer.testing import CliRunner

from pandemic import Adapters, SignatureBuilder

runner = CliRunner()
to_typer = SignatureBuilder.unpack_arguments(Adapters.to_typer)

app = typer.Typer()


def remove_command_by_func(func):
    """型が不正なコマンドを登録した場合、後続のテストが全て失敗してしまうので、テストが完了したら削除する。"""
    commands = [
        x for x in app.registered_commands if x.callback.__name__ == "type_literal"
    ]
    assert len(commands) == 1
    app.registered_commands.remove(commands[0])


@app.command()
def func0():
    pass


def test_func0():
    result = runner.invoke(app, [])
    assert result.exit_code == 0


@app.command()
def func1(name: str, city: Optional[str] = None):
    typer.echo(f"{name}")
    typer.echo(f"{city}")


def test_func1():
    result = runner.invoke(app, ["func1", "msg1", "--city", "msg2"])
    assert "msg1" in result.stdout
    assert "msg2" in result.stdout
    assert result.exit_code == 0


def test_func2():
    @app.command()
    @to_typer
    def func2(msg: str):
        typer.echo(f"{msg}")

    result = runner.invoke(app, ["func2", "msg1"])
    assert "msg1" in result.stdout
    assert result.exit_code == 0


@app.command()
@to_typer
def func3(name: str):
    pass


def test_func3():
    result = runner.invoke(app, ["func3", "msg1"])
    assert result.exit_code == 0


def test_typer_unsupport_type():
    """typerのサポート型をテストする。"""

    @app.command()
    def type_literal(log_level: Literal["INFO", "DEBUG"]):
        pass

    with pytest.raises(RuntimeError, match="Type not yet supported"):
        result = runner.invoke(app, ["type_literal", "DEBUG"])

    remove_command_by_func(type_literal)

    from datetime import datetime
    from enum import Enum
    from pathlib import Path
    from uuid import UUID

    from typer.main import ParameterInfo, get_click_type
    from typer.models import FileBinaryRead, FileBinaryWrite, FileText, FileTextWrite

    dummy = ParameterInfo()
    assert get_click_type(annotation=str, parameter_info=dummy)
    assert get_click_type(annotation=int, parameter_info=dummy)
    assert get_click_type(annotation=float, parameter_info=dummy)
    assert get_click_type(annotation=bool, parameter_info=dummy)
    assert get_click_type(annotation=UUID, parameter_info=dummy)
    assert get_click_type(annotation=datetime, parameter_info=dummy)
    assert get_click_type(annotation=Path, parameter_info=dummy)
    assert get_click_type(annotation=FileTextWrite, parameter_info=dummy)
    assert get_click_type(annotation=FileText, parameter_info=dummy)
    assert get_click_type(annotation=FileBinaryRead, parameter_info=dummy)
    assert get_click_type(annotation=FileBinaryWrite, parameter_info=dummy)
    assert get_click_type(annotation=Enum, parameter_info=dummy)

    with pytest.raises(RuntimeError, match="Type not yet supported"):
        assert get_click_type(annotation=Literal["INFO", "DEBUG"], parameter_info=dummy)


class Input(BaseModel):
    name: str
    number: int
    log_level: Literal["INFO", "DEBUG"] = "INFO"


@app.command()
@to_typer
def func4(name: str, number: int, log_level: Literal["INFO", "DEBUG"] = "INFO"):
    pass


@app.command()
@to_typer
def func5(input: Input):
    pass


def test_func4_func5_is_same():
    params1 = inspect.signature(func4).parameters
    params2 = inspect.signature(func5).parameters

    def assert_attr(params):
        if param := params["name"]:
            assert param.annotation is str
            assert param.default is inspect._empty

        if param := params["number"]:
            assert param.annotation is int
            assert param.default is inspect._empty

        if param := params["log_level"]:
            assert param.annotation.__name__ is "LiteralEnum"  # convert literal to enum
            assert param.default == "INFO"

    assert_attr(params1)
    assert_attr(params2)

    result = runner.invoke(app, ["func4", "msg1", "20", "--log-level", "DEBUG"])
    assert result.exit_code == 0

    result = runner.invoke(app, ["func5", "msg1", "20", "--log-level", "DEBUG"])
    assert result.exit_code == 0
