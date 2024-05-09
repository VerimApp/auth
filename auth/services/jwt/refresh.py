from abc import ABC, abstractmethod

from .create import ICreateJWTTokens
from services.authenticate import IAuthenticate
from schemas import JWTTokensSchema, RefreshTokensSchema
from utils.types import UserType


class IRefreshJWTTokens(ABC):
    @abstractmethod
    async def __call__(self, entry: RefreshTokensSchema) -> JWTTokensSchema: ...


class RefreshJWTTokens(IRefreshJWTTokens):
    def __init__(
        self, authenticate: IAuthenticate, create_jwt_tokens: ICreateJWTTokens
    ) -> None:
        self.authenticate = authenticate
        self.create_jwt_tokens = create_jwt_tokens

    async def __call__(self, entry: RefreshTokensSchema) -> JWTTokensSchema:
        return self.create_jwt_tokens(user=await self._get_user(entry.refresh))

    async def _get_user(self, refresh: str) -> UserType:
        return await self.authenticate(refresh, access=False)
