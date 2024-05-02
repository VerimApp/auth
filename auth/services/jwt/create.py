from abc import ABC, abstractmethod
from datetime import timedelta

import jwt

from schemas import JWTTokensSchema
from config import settings
from utils.types import UserType
from utils.time import get_current_time


class ICreateJWTTokens(ABC):
    @abstractmethod
    def __call__(self, user: UserType) -> JWTTokensSchema: ...


class CreateJWTTokens(ICreateJWTTokens):
    def __call__(self, user: UserType) -> JWTTokensSchema:
        return JWTTokensSchema(
            access=self._make_access(user), refresh=self._make_refresh(user)
        )

    def _make_access(self, user: UserType) -> str:
        current_time = get_current_time()
        payload = {
            "user": user.id,
            "exp": (
                current_time + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME)
            ).timestamp(),
            "created_at": current_time.timestamp(),
        }
        return jwt.encode(
            payload=payload,
            key=settings.ACCESS_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

    def _make_refresh(self, user: UserType) -> str:
        current_time = get_current_time()
        payload = {
            "user": user.id,
            "exp": (
                current_time + timedelta(minutes=settings.REFRESH_TOKEN_LIFETIME)
            ).timestamp(),
            "created_at": current_time.timestamp(),
        }
        return jwt.encode(
            payload=payload,
            key=settings.REFRESH_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )
