from abc import ABC, abstractmethod

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession

from ..validators import IValidate
from ..password import IHashPassword
from ..repo import IUserRepo
from ..codes import ICreateCode
from ..codes.types import CodeTypeEnum
from config.i18n import _
from config.settings import CONFIRM_EMAIL_CHECK_DELAY
from schemas import RegistrationSchema, CodeSentSchema
from utils.types import UserType
from utils.exceptions import Custom400Exception
from utils.time import get_current_time_with_delta


class IRegisterUser(ABC):
    @abstractmethod
    async def __call__(
        self, session: AsyncSession, entry: RegistrationSchema
    ) -> CodeSentSchema | str: ...


class RegisterUser(IRegisterUser):
    def __init__(
        self,
        create_code: ICreateCode,
        validate_username: IValidate,
        validate_password: IValidate,
        hash_password: IHashPassword,
        repo: IUserRepo,
        celery_app: Celery,
    ) -> None:
        self.create_code = create_code
        self.validate_username = validate_username
        self.validate_password = validate_password
        self.hash_password = hash_password
        self.repo = repo
        self.celery_app = celery_app

    async def __call__(
        self, session: AsyncSession, entry: RegistrationSchema
    ) -> CodeSentSchema | str:
        await self._validate_email(session, entry)
        await self._validate_username(session, entry)
        self._validate_password(entry)
        entry.password = self._hash_password(entry)
        user = await self._create_user(session, entry)
        self._send_registration_check_task(user)
        return await self._create_code(session, user)

    async def _validate_email(
        self, session: AsyncSession, entry: RegistrationSchema
    ) -> None:
        if await self.repo.email_exists(session, entry.email):
            raise Custom400Exception(_("Email is already taken."))

    async def _validate_username(
        self, session: AsyncSession, entry: RegistrationSchema
    ) -> None:
        if await self.repo.username_exists(session, entry.username):
            raise Custom400Exception(_("Username is already taken."))
        self.validate_username(entry.username, raise_exception=True)

    def _validate_password(self, entry: RegistrationSchema) -> None:
        if entry.password != entry.re_password:
            raise Custom400Exception(_("Password mismatch."))
        self.validate_password(entry.password, raise_exception=True)

    async def _create_user(
        self, session: AsyncSession, entry: RegistrationSchema
    ) -> UserType:
        return await self.repo.create(session, entry)

    def _hash_password(self, entry: RegistrationSchema) -> str:
        return self.hash_password(entry.password)

    def _send_registration_check_task(self, user: UserType) -> None:
        self.celery_app.send_task(
            "config.celery.check_email_confirmed",
            args=(user.id,),
            eta=get_current_time_with_delta(seconds=CONFIRM_EMAIL_CHECK_DELAY),
        )

    async def _create_code(
        self, session: AsyncSession, user: UserType
    ) -> CodeSentSchema | str:
        return await self.create_code(
            session, user, CodeTypeEnum.EMAIL_CONFIRM, send=True
        )
