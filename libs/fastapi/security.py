from datetime import timedelta
from typing import Dict, Mapping

import jwt
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
    SecurityScopes,
)
from passlib.context import CryptContext
from pydantic import BaseModel, SecretStr

from framework import DateTimeAware


class AccessToken(BaseModel):
    token_url: str
    secret_key: str
    algorithm: str = "HS256"
    expire_minutes: int = 30
    scopes: Dict[str, str] = {
        "me": "Read information about the current user.",
        "items": "Read items.",
    }
    _pwd_context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_oauth2_password_bearer(self) -> OAuth2PasswordBearer:
        return OAuth2PasswordBearer(
            tokenUrl=self.token_url,
            scopes=self.scopes,
        )

    def get_password_hash(self, password) -> str:
        return self._pwd_context.hash(password)

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self._pwd_context.verify(plain_password, hashed_password)

    def encode_access_token(self, data: dict, expires_minutes: int = 30) -> bytes:
        to_encode = data.copy()
        expires_delta = timedelta(minutes=self.expire_minutes)
        expire = DateTimeAware.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def decode_access_token(self, token: str) -> Mapping:
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload
