from pydantic.dataclasses import dataclass


@dataclass
class JWTTokensSchema:
    access: str
    refresh: str


@dataclass
class RefreshTokensSchema:
    refresh: str
