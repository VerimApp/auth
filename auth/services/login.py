from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from config.i18n import _
from schemas import LoginSchema, JWTTokensSchema
from .jwt import CreateJWTTokens
from .repo import IUserRepo
from .password import ICheckPassword
from utils.types import UserType
from utils.exceptions import Custom401Exception
from utils.shortcuts import get_object_or_404


class ILoginUser(ABC):
    @abstractmethod
    async def __call__(
        self, session: AsyncSession, entry: LoginSchema
    ) -> JWTTokensSchema: ...


class LoginUser(ILoginUser):
    def __init__(
        self,
        create_jwt_tokens: CreateJWTTokens,
        check_password: ICheckPassword,
        repo: IUserRepo,
    ) -> None:
        self.create_jwt_tokens = create_jwt_tokens
        self.check_password = check_password
        self.repo = repo

    async def __call__(
        self, session: AsyncSession, entry: LoginSchema
    ) -> JWTTokensSchema:
        user = await self._get_user_by_login(session, entry.login)
        self._check_password(user, entry.password)
        return self._make_tokens(user)

    async def _get_user_by_login(self, session: AsyncSession, login: str) -> UserType:
        return get_object_or_404(
            await self.repo.get_by_login(session, login), msg="User not found."
        )

    def _check_password(self, user: UserType, password: str) -> None:
        if not self.check_password(password, user.password):
            raise Custom401Exception(_("Wrong password."))

    def _make_tokens(self, user: UserType) -> JWTTokensSchema:
        return self.create_jwt_tokens(user)
