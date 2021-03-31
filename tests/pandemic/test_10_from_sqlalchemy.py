# type: ignore
from datetime import datetime, timezone
from inspect import signature
from typing import Any, Iterable, List

from sqlalchemy import (
    ARRAY,
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker
from sqlalchemy.orm.attributes import InstrumentedAttribute
from sqlalchemy.sql.type_api import TypeEngine

from pandemic import SignatureBuilder, field
from pandemic.normalizers import ModelFieldEx, Normalizers

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean)
    name = Column(String, unique=True)
    created = Column(DateTime, default=datetime.utcnow, system=True)
    data = Column(JSON, nullable=False)
    items = Column(ARRAY(String), index=True)
    # updated = Column(UtcDateTime, default=utc_now, onupdate=utc_now)

    addresses = relationship(
        "Address", back_populates="user", cascade="all, delete, delete-orphan"
    )


class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True)
    email_address = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="addresses")


def test_normalize_basic_fields():

    field: ModelFieldEx = Normalizers.from_sqlalchemy_column(User.id, 0)
    assert field.name == "id"
    assert field.type_ is int
    assert field.required == True  # primary keyはTrueとする
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == []
    assert field.is_primary_key == True
    assert field.is_nullable == False
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == False

    field = Normalizers.from_sqlalchemy_column(User.is_active, 0)
    assert field.name == "is_active"
    assert field.type_ is bool
    assert field.required == False
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == []
    assert field.is_primary_key == False
    assert field.is_nullable == True
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == False

    field = Normalizers.from_sqlalchemy_column(User.name, 0)
    assert field.name == "name"
    assert field.type_ is str
    assert field.required == False
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == []
    assert field.is_primary_key == False
    assert field.is_nullable == True
    assert field.is_system == False
    assert field.is_unique == True
    assert field.is_index == False

    field = Normalizers.from_sqlalchemy_column(User.created, 0)
    assert field.name == "created"
    assert field.type_ is datetime
    assert field.required == False
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == []
    assert field.is_primary_key == False
    assert field.is_nullable == True
    assert field.is_system == True
    assert field.is_unique == False
    assert field.is_index == False

    field = Normalizers.from_sqlalchemy_column(User.data, 0)
    assert field.name == "data"
    assert field.type_ is dict
    assert field.required == True
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == []
    assert field.is_primary_key == False
    assert field.is_nullable == False
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == False

    field = Normalizers.from_sqlalchemy_column(User.items, 0)
    assert field.name == "items"
    assert field.type_ is list  # TODO: list[str]を認識させたい
    assert field.required == False
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == []
    assert field.is_primary_key == False
    assert field.is_nullable == True
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == True

    field = Normalizers.from_sqlalchemy_column(Address.user_id, 0)
    assert field.name == "user_id"
    assert field.type_ is int
    assert field.required == False
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.relation_type == ""
    assert field.foreign_keys == ["users.id"]
    assert field.is_primary_key == False
    assert field.is_nullable == True
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == False


def test_normalize_relation_fields():
    field: ModelFieldEx = Normalizers.from_sqlalchemy_column(User.addresses, 0)
    assert field.name == "addresses"
    assert field.type_ is Iterable[Address]
    assert field.relation_type == "ONETOMANY"
    assert field.foreign_keys == []
    assert field.required == True  # primary keyはTrueとする
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.is_primary_key == False
    assert field.is_nullable == False
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == False

    field: ModelFieldEx = Normalizers.from_sqlalchemy_column(Address.user, 0)
    assert field.name == "user"
    assert field.type_ is User
    assert field.relation_type == "MANYTOONE"
    assert field.foreign_keys == []
    assert field.required == True  # primary keyはTrueとする
    assert isinstance(field.meta, InstrumentedAttribute)
    assert field.is_primary_key == False
    assert field.is_nullable == False
    assert field.is_system == False
    assert field.is_unique == False
    assert field.is_index == False

    # TODO: "ONETOONE"と"MANYTOMANY"のケースをやる
    # TODO: forigen keysが生じるケースが分からない


def test_from_sqlalchemy_model():
    sb = SignatureBuilder.from_sqlalchemy_model(Address)
    fields = {x.name: x for x in sb.get_fields()}

    assert len(fields) == 4

    if field := fields["id"]:
        assert field.type_ is int
    if field := fields["email_address"]:
        assert field.type_ is str
    if field := fields["user_id"]:
        assert field.type_ is int
    if field := fields["user"]:
        assert field.type_ is User


def test_from_sqlalchemy_declarative_base():
    signatures = SignatureBuilder.from_sqlalchemy_declarative_base(Base)
    signatures = sorted((x for x in signatures), key=lambda x: x.name)
    assert [x.name for x in signatures] == ["Address", "User"]

    model = signatures[0]
    fields = {x.name: x for x in model.get_fields()}
    assert model.name == "Address"
    assert len(fields) == 4
    assert isinstance(fields["id"].meta, InstrumentedAttribute)
    assert fields["id"].type_ == int
    assert fields["email_address"].type_ is str
    assert fields["user_id"].type_ is int
    assert fields["user"].type_ is User

    model = signatures[1]
    fields = {x.name: x for x in model.get_fields()}
    assert model.name == "User"
    assert len(fields) == 7
    assert isinstance(fields["id"].meta, InstrumentedAttribute)
    assert fields["id"].type_ == int
    assert fields["is_active"].type_ is bool
    assert fields["name"].type_ is str
    assert fields["created"].type_ is datetime
    assert fields["data"].type_ is dict
    assert fields["items"].type_ is list
    assert fields["addresses"].type_ is Iterable[Address]
