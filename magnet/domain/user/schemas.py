from typing import List, Optional

from pydantic import SecretStr

from ...commons import BaseModel


class ORM:
    orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_name: str
    scopes: List[str] = []
    token: str


class Item(BaseModel):
    Config = ORM  # type: ignore

    id: int
    title: str
    description: Optional[str] = None
    owner_id: int


class UserCreate(BaseModel):
    email: str
    password: SecretStr


class User(BaseModel):
    Config = ORM  # type: ignore

    id: int
    email: str
    # password: str # セキュリティ観点上、値を返さない
    username: str
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    is_active: bool
    items: List[Item] = []
