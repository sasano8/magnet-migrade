from typing import Any, List

from fastapi import Depends, HTTPException, Security, status
from fastapi.param_functions import Path
from jwt import PyJWTError
from pydantic import SecretStr, ValidationError, validator
from pydantic.fields import Field
from sqlalchemy.orm.session import Session

from ...commons import BaseModel, intellisense
from ...database import get_db
from .models import DenyToken, User, UserRoles
from .schemas import Token, TokenData
from .utils import (
    SecurityScopes,
    decode_access_token,
    encode_access_token,
    get_password_hash,
    oauth2_schema,
    verify_password,
)

# https://qiita.com/h_tyokinuhata/items/ab8e0337085997be04b1
credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid authentication credentials",
    headers={"WWW-Authenticate": "Bearer"},  # 認証方法
)


async def get_valid_token(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db),
) -> TokenData:
    if await is_deny_token(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer error='invalid_token'"},
        )

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        token_scopes = payload.get("scopes", [])
        if username is None:
            raise credentials_exception
        token_data = TokenData(user_name=username, scopes=token_scopes, token=token)
    except (PyJWTError, ValidationError) as e:
        raise credentials_exception
    return token_data


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db),
):
    token_data = await get_valid_token(security_scopes, token, db)

    user = User.L_get_by_name(db, name=token_data.user_name)
    if not user:
        raise credentials_exception

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"

    # 要求に必要な権限を保持しているか
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions.",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return user


async def is_deny_token(db: Session, token: str) -> bool:
    if deny := db.query(DenyToken.id).filter(DenyToken.token == token).one_or_none():
        return True
    else:
        return False


async def get_current_user_id(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db),
) -> int:
    user = await get_current_user(security_scopes, token, db)
    return user.id


async def get_current_active_user(
    current_user: User = Security(get_current_user, scopes=["me"])
) -> User:
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges",
        )
    return current_user


class _UserRoleFilter:
    def __init__(self, *args: UserRoles) -> None:
        self.roles = set(args)

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user doesn't have enough privileges",
            )
        return user


def FilterRole(*args: UserRoles) -> Any:
    """指定したロールユーザーのみにアクセス権を与える"""
    obj = _UserRoleFilter(*args)
    return Depends(obj)


@intellisense
class TryLogin(BaseModel):
    user_name: str
    password: str
    scopes: List[str]

    def do(self, db: Session):
        user = User.L_get_by_name(db, name=self.user_name)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect username.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(self.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token = encode_access_token(
            data={"sub": user.username, "scopes": self.scopes},
            expires_minutes=30,
        )
        return Token(access_token=access_token, token_type="bearer")


async def logout_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_schema),
    db: Session = Depends(get_db),
):
    token_data = await get_valid_token(security_scopes, token, db)
    if not (
        result := db.query(DenyToken.id)
        .filter(DenyToken.token == token_data.token)
        .one_or_none()
    ):
        token = DenyToken(token=token_data.token, user_name=token_data.user_name)
        token.create(db)
    # TODO: 何を返せばいいのかよく分からない
    # TODO: そもそもフロントエンド側のログアウトはトークンを破棄すればよいのでログアウト処理自体いらない
    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


@intellisense
class ModifyPassword(BaseModel):
    password: SecretStr

    @validator("password", pre=True, always=True)
    def is_validpassword(cls, v):
        if len(v) < 6:
            raise ValueError("Password should be at least 6 characters")
        return v

    @property
    def hashed_password(self):
        val = self.password.get_secret_value()
        hashed_password = get_password_hash(val)
        return hashed_password


@intellisense
class RegisterFirstAdmin(ModifyPassword):
    email: str
    password: SecretStr

    def do(self, db: Session):
        if user := db.query(User).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Application is initialized.",
            )

        user = User(
            email=self.email,
            username=self.email,
            hashed_password=self.hashed_password,
            role=UserRoles.admin,
        )
        return user.create(db)


@intellisense
class RegisterUser(ModifyPassword):
    email: str
    password: SecretStr

    def do(self, db: Session):
        user = User.L_get_by_name(db, name=self.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registerd",
            )

        user = User(
            email=self.email,
            username=self.email,
            hashed_password=self.hashed_password,
            role=UserRoles.user,
        )
        return user.create(db)


@intellisense
class ModifyUserPassword(ModifyPassword):
    user_id: int
    password: SecretStr

    def do(self, db: Session) -> User:
        raise NotImplementedError()


@intellisense
class IndexUser(BaseModel):
    def query(self, db: Session):
        return db.query(User)


@intellisense
class GetUser(BaseModel):
    id: int = Path(..., alias="user_id")

    def do(self, db: Session):
        if not (user := db.query(User).get(self.id)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user


@intellisense
class DeleteUser(BaseModel):
    id: int = Path(..., alias="user_id")

    def do(self, db: Session):
        if not (user := db.query(User).get(self.id)):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return user.delete(db)
