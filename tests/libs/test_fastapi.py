# type: ignore

import pytest
import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.ext.declarative import declarative_base

from framework import Linq
from libs.fastapi import utils


def test_utils():
    Base = declarative_base()

    class Model(Base):
        __tablename__ = "test"
        id_1 = sa.Column(sa.Integer, primary_key=True, index=True)
        id_2 = sa.Column(sa.Integer, primary_key=True, index=True)
        name = sa.Column(sa.String(255), nullable=False)

        __table_args__ = (PrimaryKeyConstraint(id_1, id_2),)

    class Repository(utils.GenericRepository[Model]):
        pass

    rep = Repository()
    query = Linq(rep.primary_keys).select(lambda field: field.name)
    assert query.compare(["id_1", "id_2"]).all()
