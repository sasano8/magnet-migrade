import functools
import traceback

import typer


def handle_error(func):
    """例外を補足して、エラーの出力処理を行う"""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except typer.Exit:
            raise
        except typer.Abort:
            raise
        except Exception as e:
            tb = traceback.TracebackException.from_exception(e)
            typer.echo("\n".join(tb.format()))
            typer.secho(str(e), bg=typer.colors.RED)
            raise typer.Exit(code=1)

    return wrapper
