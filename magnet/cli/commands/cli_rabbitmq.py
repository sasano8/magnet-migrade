import asyncio
import os
import time
from typing import List

import click
import typer

app = typer.Typer(help="Manage rabbitmq consumers.")


@app.command()
def start(app: str, reload: bool = False, debug: bool = False):
    """Enumrate key-value with dockerfm.toml."""
    start_worker(app, reload)


def start_worker(reload: bool = False, debug: bool = False, app_names: List[str] = []):
    """"１．ワーカーインスタンスを取得する。２．イベントループを開始する。３．消費を開始する。"""
    try:
        import sys

        app_name = app_names[0]

        from importlib import import_module

        cd = os.getcwd()
        module, attr = app_name.split(":")

        print("current :{}".format(cd))

        if module in sys.modules:
            sys.modules.pop(module)

        # モジュール初期化時にエラーが発生してると処理が完了してしまうため、修正されたら動くようにする。
        imported_module = None
        while not imported_module:
            try:
                imported_module = import_module(module)
            except KeyboardInterrupt as e:
                raise
            except Exception as e:
                time.sleep(3)

        app = getattr(imported_module, attr)
        consumer = app.get_consumer()
        loop = None

        try:
            loop = asyncio.new_event_loop()
            result = loop.run_until_complete(consumer.consume())

        except asyncio.CancelledError as e:
            print("非同期処理がキャンセルされました。")

        except Exception as e:
            raise

        finally:
            if loop:
                loop.close()

            if consumer:
                consumer.stop()

    except KeyboardInterrupt as e:
        print("購読を中止します")
