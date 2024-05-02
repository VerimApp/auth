from pydantic import (
    Field,
    EmailStr,
)
from pydantic.dataclasses import dataclass


@dataclass
class LoginSchema:
    login: str | EmailStr = Field(min_length=1)
    password: str = Field(min_length=1)
