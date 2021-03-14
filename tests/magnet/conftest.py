from pytest import fixture
from sqlalchemy_utils import database_exists

from magnet.__main import app
from magnet.database import Base, create_db, create_db_engine, drop_db, env, get_db

engine, override_get_db = create_db_engine(env.sqlalchemy_database_test_url)


@fixture(scope="session", autouse=True)
def override_dependency():
    drop_db(env.sqlalchemy_database_test_url)
    create_db(env.sqlalchemy_database_test_url)

    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db


def test_db():
    assert True
