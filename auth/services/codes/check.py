from abc import ABC, abstractmethod

from .types import CodeType, CodeTypeEnum
from .repo import ICodeRepo
from config import settings
from config.i18n import _
from utils.types import UserType
from utils.time import get_current_time
from utils.exceptions import Custom400Exception


class ICheckCode(ABC):
    @abstractmethod
    def __call__(
        self,
        user: UserType,
        type: CodeTypeEnum,
        code: str,
        *,
        raise_exception: bool = True
    ) -> bool: ...


class CheckCode(ICheckCode):
    def __init__(self, repo: ICodeRepo) -> None:
        self.repo = repo

    def __call__(
        self,
        user: UserType,
        type: CodeTypeEnum,
        code: str,
        *,
        raise_exception: bool = True
    ) -> bool:
        return self._is_valid(
            last_code=self._get_last_code(user, type),
            code=code,
            type=type,
            raise_exception=raise_exception,
        )

    def _get_last_code(self, user: UserType, type: CodeTypeEnum) -> CodeType | None:
        return self.repo.get_last(user.id, type)

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
