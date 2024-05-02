from typing import ClassVar, Dict, Protocol
from datetime import datetime


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict]


class UserType:
    id: int
    email: str
    username: str
    password: str
    salt: str
    first_name: str | None
    last_name: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    tokens_revoked_at: datetime | None
    email_confirmed: bool
