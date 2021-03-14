import json
import logging
from typing import (
    TYPE_CHECKING,
    Callable,
    ClassVar,
    Generic,
    Iterable,
    Type,
    TypeVar,
    cast,
)

from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine, or_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, Session, sessionmaker

from .config import DatabaseConfig
from .utils.objects import MyQuery

logger = logging.getLogger(__name__)


def json_dumps(dic: dict):
    dic = jsonable_encoder(dic)
    s = json.dumps(dic, ensure_ascii=False)
    return s


def create_get_db(session_maker) -> Callable[[], Iterable[Session]]:
    def get_db() -> Iterable[Session]:
        db: Session = session_maker()
        try:
            yield db
            db.commit()
        except Exception as e:
            try:
                db.rollback()
            except Exception as e:
                logger.critical(e, exc_info=True)
            raise
        finally:
            # noinspection PyBroadException
            try:
                # In case of uncommit, it will be rolled back implicitly
                db.close()
            except Exception as e:
                logger.critical(e, exc_info=True)

    return get_db


def create_db_engine(connection_string):
    # TODO: トランザクション分離レベルの設定とテストをする。postgreSQLのデフォルトトランザクション分離レベルはread committedです。
    # read committedは、コミットされていないデータの最新情報やレコードを、異なるトランザクションから参照することができません。
    #  https://docs.sqlalchemy.org/en/13/dialects/postgresql.html?highlight=dialect#transaction-isolation-level
    engine = create_engine(
        # SQLALCHEMY_DATABASE_URL,
        connection_string,
        connect_args={"options": "-c timezone=utc"},
        json_serializer=json_dumps,
        # コネクションプール設定
        # poolclass=QueuePool, pool_size= max_overflow
    )
    session_maker = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, query_cls=MyQuery
    )
    _get_db = create_get_db(session_maker)
    return engine, _get_db


def create_db(connection_string):
    from sqlalchemy_utils import create_database

    engine, get_db = create_db_engine(connection_string)
    logger.info(f"Created database: {engine.url.database}")
    create_database(connection_string)


def drop_db(connection_string):
    from sqlalchemy_utils import database_exists, drop_database

    engine, get_db = create_db_engine(connection_string)
    logger.info(f"Dropped database: {engine.url.database}")

    if database_exists(connection_string):
        drop_database(connection_string)


# initialize
env = DatabaseConfig()
engine, get_db = create_db_engine(env.sqlalchemy_database_url)


if TYPE_CHECKING:
    from .utils.objects import Entity

    tmp = declarative_base()

    class Base(Entity, tmp):
        pass


else:
    from .utils.objects import Entity

    Base = declarative_base(cls=Entity)
