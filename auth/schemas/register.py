from pydantic import EmailStr, Field
from pydantic.dataclasses import dataclass

from config import settings


@dataclass
class RegistrationSchema:
    email: EmailStr
    username: str
    password: str
    re_password: str


@dataclass
class CodeSentSchema:
    email: EmailStr
    message: str


@dataclass
class ConfirmRegistrationSchema:
    email: EmailStr
    code: str = Field(
        min_length=settings.CONFIRMATION_CODE_LENGTH,
        max_length=settings.CONFIRMATION_CODE_LENGTH,
    )


@dataclass
class RepeatRegistrationCodeSchema:
    email: EmailStr
