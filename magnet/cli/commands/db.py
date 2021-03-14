import os

import typer

from alembic.config import Config as AlembicConfig
from alembic.config import command as alembic_command
from magnet.cli.errors import handle_error

app = typer.Typer()


def command(func):
    wrapped = handle_error(func)
    return app.command()(wrapped)


@command
def show_alembic_config():
    """alembicのコンフィグを表示します。"""
    config = None

    with open(get_alembic_cfg_path(), mode="r") as f:
        config = f.read()

    typer.echo(config)


@command
def create():
    """データベースを作成します。"""
    from magnet.database import create_db, env

    create_db(env.sqlalchemy_database_url)


@command
def drop():
    """データベースを削除します。"""
    from magnet.database import drop_db, env

    drop_db(env.sqlalchemy_database_url)


@command
def makemigrations():
    """データベースとソースコードの差分からマイグレーションファイルを生成します。
    [注意]差分検出は完全ではありません。
    """
    from framework import DateTimeAware

    alembic_cfg = get_alembic_cfg()
    rev_id = DateTimeAware.utcnow().strftime("%Y%m%d_%H%M%S")
    alembic_command.revision(alembic_cfg, head="head", autogenerate=True, rev_id=rev_id)


@command
def migrate():
    """マイグレーションファイルをデータベースに適用します。"""
    alembic_cfg = get_alembic_cfg()
    alembic_command.upgrade(alembic_cfg, revision="head")


@command
def export_spec(
    er_file_path: str = "doc/er.png", tables_file_path: str = "doc/tables.md"
):
    """テーブル一覧とER図を生成します。"""
    import eralchemy

    from magnet.database import Base

    eralchemy.render_er(Base, er_file_path)
    typer.echo(f"generated {er_file_path=}")

    markdown = get_table_define_as_markdown(Base)
    with open(tables_file_path, mode="w") as f:
        f.write(markdown)

    typer.echo(f"generated {tables_file_path=}")


# utils
def get_alembic_cfg_path() -> str:
    cd = os.getcwd()
    return os.path.join(cd, "alembic.ini")


def get_alembic_cfg():
    alembic_path = get_alembic_cfg_path()
    alembic_cfg = AlembicConfig(alembic_path)
    return alembic_cfg


def get_table_define_as_markdown(base):
    tables = [x for x in base.metadata.tables.values()]
    arr = []

    for table in tables:
        """
        'key',
        'name',
        'table',
        'type',
        'is_literal',
        'primary_key',
        'nullable',
        'default',
        'server_default',
        'server_onupdate',
        'index',
        'unique',
        'system',
        'doc',
        'onupdate',
        'autoincrement',
        'constraints',
        'foreign_keys',
        'comment',
        'computed',
        '_creation_order',
        'dispatch',
        'proxy_set',
        'description',
        'comparator',
        '_cloned_set',
        '_from_objects',
        '_label',
        '_key_label',
        '_render_label_in_columns_clause'
        """

        arr.append("## " + table.name)
        if table.comment:
            arr.append(table.comment)
            arr.append("")
        arr.append(
            "| name | type | pk | unique | index | nullable | default | comment |"
        )
        arr.append("| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |")
        for column in table._columns.values():

            dic = create_column_info_as_dict(
                name=column.name,
                type_=column.type,
                pk=column.primary_key,
                unique=column.unique,
                index=column.index,
                nullable=column.nullable,
                default=column.default,
                comment=column.comment,
            )

            s = "| {name} | {type} | {pk} | {unique} | {index} | {nullable} | {default} | {comment} |".format(
                **dic
            )
            arr.append(s)

        arr.append("")

    return "\n".join(arr)


def create_column_info_as_dict(
    name, type_, pk, unique, index, nullable, default, comment
):
    def get_value_or_empty(value):
        if value is None:
            return ""
        else:
            return value

    def get_str_or_ohter(value):
        if isinstance(value, str) and value == "":
            return '""'

        return value

    try:
        type_ = str(type_)
    except:
        # JSONカラムの場合、なぜか文字列化できない。それ以外のカラムで、発生するかは知らん。
        type_ = type(type_).__name__

    # 設計書にNoneが表示されるのが煩わしいため空文字にする
    return dict(
        name=get_value_or_empty(name),
        type=get_value_or_empty(type_),
        pk="x" if pk else "",
        unique="x" if unique else "",
        index="x" if index else "",
        nullable="x" if nullable else "",
        default=get_str_or_ohter(default.arg) if default else "",
        comment=get_value_or_empty(comment),
    )
