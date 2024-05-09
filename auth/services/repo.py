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
        session: AsyncSession | None = None,
        *,
        include_not_confirmed_email: bool = False,
        as_select: bool = False,
    ) -> Result[User] | Select[User]: ...

    @abstractmethod
    async def create(self, entry: RegistrationSchema) -> User: ...

    @abstractmethod
    async def update(self, user: User, values: Dict) -> None: ...

    @abstractmethod
    async def delete(self, user: User) -> None: ...

    @abstractmethod
    async def email_exists(self, email: str) -> bool: ...

    @abstractmethod
    async def username_exists(self, username: str) -> bool: ...

    @abstractmethod
    async def get_by_login(self, login: str) -> User | None: ...

    @abstractmethod
    async def get_by_id(self, id: int) -> User | None: ...

    @abstractmethod
    async def get_by_email(
        self, email: str, *, include_not_confirmed_email: bool = False
    ) -> User | None: ...
