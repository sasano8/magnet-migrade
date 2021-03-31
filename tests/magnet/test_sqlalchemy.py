import sqlalchemy as sa

from framework import undefined
from magnet.domain.user.models import User

from .conftest import override_get_db


def test_binary():
    for db in override_get_db():
        query = db.query(User)
        query = query.where(User.id == 1)
        assert len(query._where_criteria[0]._select_iterable) == 1

    for db in override_get_db():
        query = db.query(User)
        query = query.where(User.id == undefined)
        assert not query._where_criteria

    for db in override_get_db():
        query = db.query(User)
        query = query.where(User.id is undefined)
        assert str(query._where_criteria[0]) == "false"

    for db in override_get_db():
        query = db.query(User)
        query = query.where(User.id == undefined, User.id == 2)
        assert len(query._where_criteria) == 1
        assert str(query._where_criteria[0]) == "users.id = :id_1"
        assert len(query._where_criteria[0]._select_iterable) == 1
