import sqlalchemy as sa

from framework import undefined
from magnet.domain.user.models import User

from .conftest import override_get_db


def test_binary():
    for db in override_get_db():
        query = db.query(User)
        query = query.filter(User.id == 1)
        assert len(query._criterion._select_iterable) == 1

    for db in override_get_db():
        query = db.query(User)
        query = query.filter(User.id == undefined)
        assert query._criterion is None

    for db in override_get_db():
        query = db.query(User)
        query = query.filter(User.id is undefined)
        assert str(query._criterion) == "false"

    for db in override_get_db():
        query = db.query(User)
        query = query.filter(User.id == undefined, User.id == 2)
        assert str(query._criterion) == "users.id = :id_1"
        assert len(query._criterion._select_iterable) == 1
