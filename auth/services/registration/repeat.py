from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ..codes import ICreateCode
from ..repo import IUserRepo
from ..entries import CodeTypeEnum
from config.i18n import _
from schemas import RepeatRegistrationCodeSchema, CodeSentSchema
from utils.types import UserType
from utils.exceptions import Custom400Exception
from utils.shortcuts import get_object_or_404


class IRepeatRegistrationCode(ABC):
    @abstractmethod
    async def __call__(
        self, session: AsyncSession, entry: RepeatRegistrationCodeSchema
    ) -> CodeSentSchema | str: ...


class RepeatRegistrationCode(IRepeatRegistrationCode):
    def __init__(self, create_code: ICreateCode, repo: IUserRepo) -> None:
        self.create_code = create_code
        self.repo = repo

    async def __call__(
        self, session: AsyncSession, entry: RepeatRegistrationCodeSchema
    ) -> CodeSentSchema | str:
        user = await self._get_user(session, entry)
        self._check_email_confirmed(user)
        return await self._create_code(session, user)

    async def _get_user(
        self, session: AsyncSession, entry: RepeatRegistrationCodeSchema
    ) -> UserType:
        return get_object_or_404(
            await self.repo.get_by_email(
                session, email=entry.email, include_not_confirmed_email=True
            ),
            msg="User not found.",
        )

    def _check_email_confirmed(self, user: UserType) -> None:
        if user.email_confirmed:
            raise Custom400Exception(_("Email is already confirmed"))

    async def _create_code(
        self, session: AsyncSession, user: UserType
    ) -> CodeSentSchema | str:
        return await self.create_code(
            session, user, CodeTypeEnum.EMAIL_CONFIRM, send=True
        )
