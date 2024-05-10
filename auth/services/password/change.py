from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

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
    async def __call__(
        self, session: AsyncSession, user_id: int, entry: ChangePasswordSchema
    ) -> None: ...


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

    async def __call__(
        self, session: AsyncSession, user_id: int, entry: ChangePasswordSchema
    ) -> None:
        user = await self._get_user(session, user_id)
        self._chech_current_password(user, entry.current_password)
        self._validate_new_password(entry)
        await self._set_password(session, user, entry.new_password)
        await self._revoke_jwt_tokens(session, user)

    async def _get_user(self, session: AsyncSession, user_id: int) -> UserType:
        return get_object_or_404(await self.repo.get_by_id(session, id=user_id))

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

    async def _set_password(
        self, session: AsyncSession, user: UserType, password: str
    ) -> None:
        await self.repo.update(
            session, user, {"password": self.hash_password(password)}
        )

    async def _revoke_jwt_tokens(self, session: AsyncSession, user: UserType) -> None:
        await self.revoke_jwt_tokens(session, user)
