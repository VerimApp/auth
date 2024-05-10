from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ..codes import ICreateCode
from ..repo import IUserRepo
from ..entries import CodeTypeEnum
from schemas import ResetPasswordSchema, CodeSentSchema
from utils.types import UserType
from utils.shortcuts import get_object_or_404


class IResetPassword(ABC):
    @abstractmethod
    async def __call__(
        self, session: AsyncSession, entry: ResetPasswordSchema
    ) -> CodeSentSchema | str: ...


class ResetPassword(IResetPassword):
    def __init__(self, create_code: ICreateCode, repo: IUserRepo) -> None:
        self.create_code = create_code
        self.repo = repo

    async def __call__(
        self, session: AsyncSession, entry: ResetPasswordSchema
    ) -> CodeSentSchema | str:
        user = await self._get_user(session, entry)
        return await self._create_code(session, user)

    async def _get_user(
        self, session: AsyncSession, entry: ResetPasswordSchema
    ) -> UserType:
        return get_object_or_404(
            await self.repo.get_by_email(session, entry.email), msg="User not found."
        )

    async def _create_code(
        self, session: AsyncSession, user: UserType
    ) -> CodeSentSchema | str:
        return await self.create_code(
            session, user, CodeTypeEnum.RESET_PASSWORD, send=True
        )
