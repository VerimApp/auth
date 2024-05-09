from abc import ABC, abstractmethod

from ..repo import IUserRepo
from utils.types import UserType
from utils.time import get_current_time


class IRevokeJWTTokens(ABC):
    @abstractmethod
    async def __call__(self, user: UserType) -> None: ...


class RevokeJWTTokens(IRevokeJWTTokens):
    def __init__(self, repo: IUserRepo) -> None:
        self.repo = repo

    async def __call__(self, user: UserType) -> None:
        await self._update_revokation_time(user)

    async def _update_revokation_time(self, user: UserType) -> None:
        await self.repo.update(user, {"tokens_revoked_at": get_current_time()})
