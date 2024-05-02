from enum import Enum
from datetime import datetime


class CodeTypeEnum(Enum):
    EMAIL_CONFIRM = "EMAIL_CONFIRM"
    RESET_PASSWORD = "RESET_PASSWORD"


class CodeType:
    id: int
    user_id: int
    code: str
    type: CodeTypeEnum
    created_at: datetime
