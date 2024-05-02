from pydantic.dataclasses import dataclass
from pydantic import EmailStr, Field


@dataclass
class ChangePasswordSchema:
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=1)
    re_new_password: str = Field(min_length=1)


@dataclass
class ResetPasswordSchema:
    email: EmailStr = Field(min_length=1)


@dataclass
class ResetPasswordConfirmSchema:
    email: EmailStr = Field(min_length=1)
    code: str = Field(min_length=1)
    new_password: str = Field(min_length=1)
    re_new_password: str = Field(min_length=1)
