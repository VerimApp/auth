from abc import ABC, abstractmethod

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
    def __call__(self, entry: RepeatRegistrationCodeSchema) -> CodeSentSchema | str: ...


class RepeatRegistrationCode(IRepeatRegistrationCode):
    def __init__(self, create_code: ICreateCode, repo: IUserRepo) -> None:
        self.create_code = create_code
        self.repo = repo

    def __call__(self, entry: RepeatRegistrationCodeSchema) -> CodeSentSchema | str:
        user = self._get_user(entry)
        self._check_email_confirmed(user)
        return self._create_code(user)

    def _get_user(self, entry: RepeatRegistrationCodeSchema) -> UserType:
        return get_object_or_404(
            self.repo.get_by_email(email=entry.email, include_not_confirmed_email=True),
            msg="User not found.",
        )

    def _check_email_confirmed(self, user: UserType) -> None:
        if user.email_confirmed:
            raise Custom400Exception(_("Email is already confirmed"))

    def _create_code(self, user: UserType) -> CodeSentSchema | str:
        return self.create_code(user, CodeTypeEnum.EMAIL_CONFIRM, send=True)
