from abc import abstractmethod

from .types import CodeTypeEnum
from ..entries import CreateCodeEntry
from models.codes import Code
from utils.repo import IRepo


class ICodeRepo(IRepo):
    @abstractmethod
    async def create(self, entry: CreateCodeEntry) -> Code: ...

    @abstractmethod
    async def get_last(self, user_id: int, type: CodeTypeEnum) -> Code | None: ...
