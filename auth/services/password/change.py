from abc import ABC, abstractmethod

from .check import ICheckPassword
from .hash import IHashPassword
from ..jwt import IRevokeJWTTokens
from ..validators import IValidate
from ..repo import IUserRepo
from schemas import ChangePasswordSchema
from utils.types import UserType
from utils.exceptions import Custom400Exception
from utils.shortcuts import get_object_or_404
from config.i18n import _


class IChangePassword(ABC):
    @abstractmethod
    def __call__(self, user_id: int, entry: ChangePasswordSchema) -> None: ...


class ChangePassword(IChangePassword):
    def __init__(
        self,
        check_password: ICheckPassword,
        validate_password: IValidate,
        hash_password: IHashPassword,
        revoke_jwt_tokens: IRevokeJWTTokens,
        repo: IUserRepo,
    ) -> None:
        self.check_password = check_password
        self.validate_password = validate_password
        self.hash_password = hash_password
        self.revoke_jwt_tokens = revoke_jwt_tokens
        self.repo = repo

    def __call__(self, user_id: int, entry: ChangePasswordSchema) -> None:
        user = self._get_user(user_id)
        self._chech_current_password(user, entry.current_password)
        self._validate_new_password(entry)
        self._set_password(user, entry.new_password)
        self._revoke_jwt_tokens(user)

    def _get_user(self, user_id: int) -> UserType:
        return get_object_or_404(self.repo.get_by_id(id=user_id))

    def _chech_current_password(self, user: UserType, password: str) -> None:
        if not self.check_password(password, user.password):
            raise Custom400Exception(_("Wrong password."))

    def _validate_new_password(self, entry: ChangePasswordSchema) -> None:
        if entry.current_password == entry.new_password:
            raise Custom400Exception(
                _("Password must be different from the current one.")
            )
        if entry.new_password != entry.re_new_password:
            raise Custom400Exception(_("Password mismatch."))
        self.validate_password(entry.new_password, raise_exception=True)

    def _set_password(self, user: UserType, password: str) -> None:
        self.repo.update(user, {"password": self.hash_password(password)})

    def _revoke_jwt_tokens(self, user: UserType) -> None:
        self.revoke_jwt_tokens(user)
