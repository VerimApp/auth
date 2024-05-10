from abc import abstractmethod
from typing import Dict

from sqlalchemy import Select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import RegistrationSchema
from models.users import User
from utils.repo import IRepo


class IUserRepo(IRepo):
    @abstractmethod
    async def all(
        self,
        session: AsyncSession,
        *,
        include_not_confirmed_email: bool = False,
        as_select: bool = False,
    ) -> Result[User] | Select[User]: ...

    @abstractmethod
    async def create(
        self, session: AsyncSession, entry: RegistrationSchema
    ) -> User: ...

    @abstractmethod
    async def update(self, session: AsyncSession, user: User, values: Dict) -> None: ...

    @abstractmethod
    async def delete(self, session: AsyncSession, user: User) -> None: ...

    @abstractmethod
    async def email_exists(self, session: AsyncSession, email: str) -> bool: ...

    @abstractmethod
    async def username_exists(self, session: AsyncSession, username: str) -> bool: ...

    @abstractmethod
    async def get_by_login(self, session: AsyncSession, login: str) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, session: AsyncSession, id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
        *,
        include_not_confirmed_email: bool = False,
    ) -> User | None: ...
