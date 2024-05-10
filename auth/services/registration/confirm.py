from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ..jwt import ICreateJWTTokens
from ..codes import ICheckCode
from ..repo import IUserRepo
from ..entries import CodeTypeEnum
from config.i18n import _
from schemas import ConfirmRegistrationSchema, JWTTokensSchema
from utils.types import UserType
from utils.exceptions import Custom400Exception
from utils.shortcuts import get_object_or_404


class IConfirmRegistration(ABC):
    @abstractmethod
    async def __call__(self, session: AsyncSession, entry: ConfirmRegistrationSchema) -> JWTTokensSchema: ...


class ConfirmRegistration(IConfirmRegistration):
    def __init__(
        self,
        create_jwt_tokens: ICreateJWTTokens,
        check_code: ICheckCode,
        repo: IUserRepo,
    ) -> None:
        self.create_jwt_tokens = create_jwt_tokens
        self.check_code = check_code
        self.repo = repo

    async def __call__(self, session: AsyncSession, entry: ConfirmRegistrationSchema) -> JWTTokensSchema:
        user = await self._get_user(session, entry.email)
        if user.email_confirmed:
            raise Custom400Exception(_("Email is already confirmed"))
        await self._check_code(session, user, entry.code)
        await self._update_user(session, user)
        return self._create_tokens(user)

    async def _get_user(self, session: AsyncSession, email: str) -> UserType:
        return get_object_or_404(
            await self.repo.get_by_email(session, email, include_not_confirmed_email=True),
            msg="User not found.",
        )

    async def _check_code(self, session: AsyncSession, user: UserType, code: str) -> None:
        await self.check_code(session, user=user, type=CodeTypeEnum.EMAIL_CONFIRM, code=code)

    async def _update_user(self, session: AsyncSession, user: UserType) -> None:
        await self.repo.update(session, user, values={"email_confirmed": True})

    def _create_tokens(self, user: UserType) -> JWTTokensSchema:
        return self.create_jwt_tokens(user)
