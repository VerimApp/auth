from abc import ABC, abstractmethod

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
    def __call__(self, entry: ConfirmRegistrationSchema) -> JWTTokensSchema: ...


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

    def __call__(self, entry: ConfirmRegistrationSchema) -> JWTTokensSchema:
        user = self._get_user(entry.email)
        if user.email_confirmed:
            raise Custom400Exception(_("Email is already confirmed"))
        self._check_code(user, entry.code)
        self._update_user(user)
        return self._create_tokens(user)

    def _get_user(self, email: str) -> UserType:
        return get_object_or_404(
            self.repo.get_by_email(email, include_not_confirmed_email=True),
            msg="User not found.",
        )

    def _check_code(self, user: UserType, code: str) -> None:
        self.check_code(user=user, type=CodeTypeEnum.EMAIL_CONFIRM, code=code)

    def _update_user(self, user: UserType) -> None:
        self.repo.update(user, values={"email_confirmed": True})

    def _create_tokens(self, user: UserType) -> JWTTokensSchema:
        return self.create_jwt_tokens(user)
