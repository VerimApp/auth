from abc import ABC, abstractmethod

import bcrypt


ENCODING = "utf-8"


class ICheckPassword(ABC):
    @abstractmethod
    def __call__(self, plain_pwd: str, hashed_pwd: str) -> bool:
        ...


class CheckPassword(ICheckPassword):
    def __call__(self, plain_pwd: str, hashed_pwd: str) -> bool:
        return bcrypt.checkpw(plain_pwd.encode(ENCODING), hashed_pwd.encode(ENCODING))
