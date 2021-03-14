from __future__ import annotations

from enum import Enum
from typing import Type, Union

import sqlalchemy as sa
from sqlalchemy.orm import load_only, relationship

from ...commons import intellisense
from ...database import Base, Session
from ...models import TimeStampMixin


class UserRoles(str, Enum):
    admin = "admin"
    poweruser = "poweruser"
    user = "user"


@intellisense
class User(Base, TimeStampMixin):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String, unique=True, index=True)
    hashed_password = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True, index=True)
    full_name = sa.Column(sa.String, nullable=False, default="")
    role = sa.Column(sa.String, nullable=False, default=UserRoles.user)
    disabled = sa.Column(sa.Boolean, default=False)
    is_active = sa.Column(sa.Boolean, default=True)
    is_test = sa.Column(sa.Boolean, default=True)

    items = relationship("Item", back_populates="owner")

    @property
    def is_admin(self):
        return self.role == UserRoles.admin

    @property
    def is_poweruser(self):
        return self.role == UserRoles.poweruser or self.role == UserRoles.admin

    @classmethod
    def L_get_by_name(cls, db: Session, *, name) -> Union[User, None]:
        return db.query(cls).filter(cls.username == name).one_or_none()


class Item(Base):
    __tablename__ = "items"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String, index=True)
    description = sa.Column(sa.String, index=True)
    owner_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")


class DenyToken(Base):
    __tablename__ = "deny_tokens"
    id = sa.Column(sa.Integer, primary_key=True)
    token = sa.Column(sa.String(255), unique=True)
    user_name = sa.Column(sa.String(255))
