from abc import ABC, abstractmethod

from ..repo import IUserRepo
from utils.types import UserType
from utils.time import get_current_time


class IRevokeJWTTokens(ABC):
    @abstractmethod
    def __call__(self, user: UserType) -> None:
        ...


class RevokeJWTTokens(IRevokeJWTTokens):
    def __init__(self, repo: IUserRepo) -> None:
        self.repo = repo

    def __call__(self, user: UserType) -> None:
        self._update_revokation_time(user)

    def _update_revokation_time(self, user: UserType) -> None:
        self.repo.update(user, {"tokens_revoked_at": get_current_time()})
