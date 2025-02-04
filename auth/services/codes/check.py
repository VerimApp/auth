from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from .types import CodeType, CodeTypeEnum
from .repo import ICodeRepo
from config import settings
from config.i18n import _
from utils.types import UserType
from utils.time import get_current_time
from utils.exceptions import Custom400Exception


class ICheckCode(ABC):
    @abstractmethod
    async def __call__(
        self,
        session: AsyncSession,
        user: UserType,
        type: CodeTypeEnum,
        code: str,
        *,
        raise_exception: bool = True
    ) -> bool: ...


class CheckCode(ICheckCode):
    def __init__(self, repo: ICodeRepo) -> None:
        self.repo = repo

    async def __call__(
        self,
        session: AsyncSession,
        user: UserType,
        type: CodeTypeEnum,
        code: str,
        *,
        raise_exception: bool = True
    ) -> bool:
        return self._is_valid(
            last_code=await self._get_last_code(session, user, type),
            code=code,
            type=type,
            raise_exception=raise_exception,
        )

    async def _get_last_code(
        self, session: AsyncSession, user: UserType, type: CodeTypeEnum
    ) -> CodeType | None:
        return await self.repo.get_last(session, user.id, type)

    def _is_valid(
        self,
        last_code: CodeType | None,
        code: str,
        type: CodeTypeEnum,
        raise_exception: bool,
    ) -> bool:
        if (
            not last_code
            or (get_current_time() - last_code.created_at).seconds
            >= {
                CodeTypeEnum.EMAIL_CONFIRM: settings.CONFIRM_EMAIL_CODE_DURATION,
                CodeTypeEnum.RESET_PASSWORD: settings.RESET_PASSWORD_CODE_DURATION,
            }.get(type)
            or last_code.code != code
        ):
            if raise_exception:
                raise Custom400Exception(_("Code is not correct."))
            return False
        return True
