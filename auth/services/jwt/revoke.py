from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from ..repo import IUserRepo
from utils.types import UserType
from utils.time import get_current_time


class IRevokeJWTTokens(ABC):
    @abstractmethod
    async def __call__(self, session: AsyncSession, user: UserType) -> None: ...


class RevokeJWTTokens(IRevokeJWTTokens):
    def __init__(self, repo: IUserRepo) -> None:
        self.repo = repo

    async def __call__(self, session: AsyncSession, user: UserType) -> None:
        await self._update_revokation_time(session, user)

    async def _update_revokation_time(
        self, session: AsyncSession, user: UserType
    ) -> None:
        await self.repo.update(session, user, {"tokens_revoked_at": get_current_time()})
