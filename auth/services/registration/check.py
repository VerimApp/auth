import logging
from abc import ABC, abstractmethod

from ..repo import IUserRepo
from utils.types import UserType


logger = logging.getLogger("auth")


class ICheckRegistration(ABC):
    @abstractmethod
    def __call__(self, user_id: int) -> bool | None: ...


class CheckRegistration(ICheckRegistration):
    def __init__(self, repo: IUserRepo) -> None:
        self.repo = repo

    def __call__(self, user_id: int) -> bool | None:
        user = self._get_user(user_id)
        if user is None:
            logger.info(
                "Registration checking ended up with not found user.",
                extra={"user_id": user_id},
            )
            return None

        if not self._email_confirmed(user):
            self._delete_user(user)
            logger.info(
                "Registration checking ended up with user deletion.",
                extra={"user_id": user_id},
            )
            return False
        logger.info(
            "Registration checking ended up with email confirmation.",
            extra={"user_id": user_id},
        )
        return True

    def _get_user(self, user_id: int) -> UserType | None:
        return self.repo.get_by_id(user_id)

    def _email_confirmed(self, user: UserType) -> bool:
        return user.email_confirmed

    def _delete_user(self, user: UserType) -> None:
        self.repo.delete(user)
