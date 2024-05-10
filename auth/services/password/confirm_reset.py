from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ..codes import ICheckCode
from ..repo import IUserRepo
from ..validators import IValidate
from ..entries import CodeTypeEnum
from ..password import IHashPassword, ICheckPassword
from config.i18n import _
from schemas import ResetPasswordConfirmSchema
from utils.types import UserType
from utils.shortcuts import get_object_or_404
from utils.exceptions import Custom400Exception


class IConfirmResetPassword(ABC):
    @abstractmethod
    async def __call__(
        self, session: AsyncSession, entry: ResetPasswordConfirmSchema
    ) -> None: ...


class ConfirmResetPassword(IConfirmResetPassword):
    def __init__(
        self,
        check_code: ICheckCode,
        validate_password: IValidate,
        hash_password: IHashPassword,
        check_password: ICheckPassword,
        repo: IUserRepo,
    ) -> None:
        self.check_code = check_code
        self.validate_password = validate_password
        self.hash_password = hash_password
        self.check_password = check_password
        self.repo = repo

    async def __call__(
        self, session: AsyncSession, entry: ResetPasswordConfirmSchema
    ) -> None:
        user = await self._get_user(session, entry)
        await self._check_code(session, user, entry.code)
        self._validate_password(user, entry)
        await self._set_password(session, user, entry.new_password)

    async def _get_user(
        self, session: AsyncSession, entry: ResetPasswordConfirmSchema
    ) -> UserType:
        return get_object_or_404(
            await self.repo.get_by_email(session, entry.email), msg="User not found."
        )

    async def _check_code(
        self, session: AsyncSession, user: UserType, code: str
    ) -> None:
        await self.check_code(session, user, CodeTypeEnum.RESET_PASSWORD, code)

    def _validate_password(
        self, user: UserType, entry: ResetPasswordConfirmSchema
    ) -> None:
        if entry.new_password != entry.re_new_password:
            raise Custom400Exception(_("Password mismatch."))
        if self.check_password(entry.new_password, user.password):
            raise Custom400Exception(_("New pasword must be different from old one."))
        self.validate_password(entry.new_password, raise_exception=True)

    async def _set_password(
        self, session: AsyncSession, user: UserType, password: str
    ) -> None:
        await self.repo.update(
            session, user=user, values={"password": self._hash_password(password)}
        )

    def _hash_password(self, password: str) -> str:
        return self.hash_password(password)
