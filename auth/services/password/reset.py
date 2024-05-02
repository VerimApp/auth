from abc import ABC, abstractmethod

from ..codes import ICreateCode
from ..repo import IUserRepo
from ..entries import CodeTypeEnum
from schemas import ResetPasswordSchema, CodeSentSchema
from utils.types import UserType
from utils.shortcuts import get_object_or_404


class IResetPassword(ABC):
    @abstractmethod
    def __call__(self, entry: ResetPasswordSchema) -> CodeSentSchema | str: ...


class ResetPassword(IResetPassword):
    def __init__(self, create_code: ICreateCode, repo: IUserRepo) -> None:
        self.create_code = create_code
        self.repo = repo

    def __call__(self, entry: ResetPasswordSchema) -> CodeSentSchema | str:
        user = self._get_user(entry)
        return self._create_code(user)

    def _get_user(self, entry: ResetPasswordSchema) -> UserType:
        return get_object_or_404(
            self.repo.get_by_email(entry.email), msg="User not found."
        )

    def _create_code(self, user: UserType) -> CodeSentSchema | str:
        return self.create_code(user, CodeTypeEnum.RESET_PASSWORD, send=True)
