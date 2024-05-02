from abc import abstractmethod
from typing import Dict

from sqlalchemy.orm import Query

from schemas import RegistrationSchema
from utils.types import UserType
from utils.repo import IRepo


class IUserRepo(IRepo):
    @abstractmethod
    def all(self, *, include_not_confirmed_email: bool = False) -> Query: ...

    @abstractmethod
    def create(self, entry: RegistrationSchema) -> UserType: ...

    @abstractmethod
    def update(self, user: UserType, values: Dict) -> None: ...

    @abstractmethod
    def delete(self, user: UserType) -> None: ...

    @abstractmethod
    def email_exists(self, email: str) -> bool: ...

    @abstractmethod
    def username_exists(self, username: str) -> bool: ...

    @abstractmethod
    def get_by_login(self, login: str) -> UserType | None: ...

    @abstractmethod
    def get_by_id(self, id: int) -> UserType | None: ...

    @abstractmethod
    def get_by_email(
        self, email: str, *, include_not_confirmed_email: bool = False
    ) -> UserType | None: ...
