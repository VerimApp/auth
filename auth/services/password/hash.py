from abc import ABC, abstractmethod

import bcrypt


ENCODING = "utf-8"


class IHashPassword(ABC):
    @abstractmethod
    def __call__(self, password: str) -> str:
        ...


class HashPassword(IHashPassword):
    def __call__(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(ENCODING), bcrypt.gensalt()).decode(
            ENCODING
        )
