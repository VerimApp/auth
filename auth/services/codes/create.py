from abc import ABC, abstractmethod

from ..entries import CreateCodeEntry, SendCodeEntry
from .types import CodeType, CodeTypeEnum
from .repo import ICodeRepo
from .send import ISendCode
from config import settings
from config.i18n import _
from schemas import CodeSentSchema
from utils.types import UserType
from utils.time import get_current_time
from utils.exceptions import Custom400Exception
from utils.random import get_random_string


class ICreateCode(ABC):
    @abstractmethod
    def __call__(
        self, user: UserType, type: CodeTypeEnum, *, send: bool = True
    ) -> str | CodeSentSchema: ...


class CreateCode(ICreateCode):
    code_duration_map = {
        CodeTypeEnum.EMAIL_CONFIRM: settings.CONFIRM_EMAIL_CODE_DURATION,
        CodeTypeEnum.RESET_PASSWORD: settings.RESET_PASSWORD_CODE_DURATION,
    }

    def __init__(self, send_code: ISendCode, repo: ICodeRepo) -> None:
        self.send_code = send_code
        self.repo = repo

    def __call__(
        self, user: UserType, type: CodeTypeEnum, *, send: bool = True
    ) -> str | CodeSentSchema:
        self._check_has_active(user, type)
        code = self._create_code(user, type)
        if send:
            return self._send_code(user.email, code)
        return code.code

    def _check_has_active(self, user: UserType, type: CodeTypeEnum) -> None:
        last_code = self.repo.get_last(user.id, type)
        if not last_code:
            return

        seconds_diff = (get_current_time() - last_code.created_at).seconds
        if seconds_diff <= self.code_duration_map[type]:
            raise Custom400Exception(
                _("New code will be available to obtain after: %(seconds)s")
                % {"seconds": self.code_duration_map[type] - seconds_diff}
            )

    def _create_code(self, user: UserType, type: CodeTypeEnum) -> CodeType:
        return self.repo.create(
            entry=CreateCodeEntry(
                user_id=user.id,
                code=get_random_string(
                    length=settings.CONFIRMATION_CODE_LENGTH,
                    allowed_characters=settings.CONFIRMATION_CODE_CHARACTERS,
                ),
                type=type,
            )
        )

    def _send_code(self, email: str, code: CodeType) -> CodeSentSchema:
        return self.send_code(
            entry=SendCodeEntry(email=email, code=code.code, type=code.type)
        )
