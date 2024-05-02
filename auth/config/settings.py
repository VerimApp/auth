import os
import string
from typing import List


JWT_ALGORITHM: str = os.environ.get("JWT_ALGORITHM", "")
ACCESS_SECRET_KEY: str = os.environ.get("ACCESS_SECRET_KEY", "")
REFRESH_SECRET_KEY: str = os.environ.get("REFRESH_SECRET_KEY", "")
ACCESS_TOKEN_LIFETIME: int = int(
    os.environ.get("ACCESS_TOKEN_LIFETIME", 1)
)  # in minutes
REFRESH_TOKEN_LIFETIME: int = int(
    os.environ.get("REFRESH_TOKEN_LIFETIME", 1)
)  # in minutes

TIMEZONE: str = os.environ.get("TIMEZONE", "Europe/Moscow")

PASSWORD_SALT_LENGTH: int = int(os.environ.get("PASSWORD_SALT_LENGTH", 20))
PASSWORD_HASH_ITERATIONS: int = int(os.environ.get("PASSWORD_HASH_ITERATIONS", 100100))

DB_USER: str = os.environ.get("DB_USER", "")
DB_PASSWORD: str = os.environ.get("DB_PASSWORD", "")
DB_NAME: str = os.environ.get("DB_NAME", "")
DB_HOST: str = os.environ.get("DB_HOST", "")
DB_PORT: str = os.environ.get("DB_PORT", "")
DATABASE_URL: str = os.environ.get("DATABASE_URL", "")

TEST_DB_USER: str = os.environ.get("TEST_DB_USER", "")
TEST_DB_PASSWORD: str = os.environ.get("TEST_DB_PASSWORD", "")
TEST_DB_NAME: str = os.environ.get("TEST_DB_NAME", "")
TEST_DB_HOST: str = os.environ.get("TEST_DB_HOST", "")
TEST_DB_PORT: str = os.environ.get("TEST_DB_PORT", "")
TEST_DATABASE_URL: str = os.environ.get("TEST_DATABASE_URL", "")

USERNAME_MIN_LENGTH: int = int(os.environ.get("USERNAME_MIN_LENGTH", 0))
USERNAME_MAX_LENGTH: int = int(os.environ.get("USERNAME_MAX_LENGTH", 0))
USERNAME_ALLOWED_SPECIAL_CHARACTERS: str = os.environ.get(
    "USERNAME_ALLOWED_SPECIAL_CHARACTERS", ""
)
USERNAME_ALLOWED_CHARACTERS: str = (
    string.ascii_letters + string.digits + USERNAME_ALLOWED_SPECIAL_CHARACTERS
)

PASSWORD_MIN_LENGTH: int = int(os.environ.get("PASSWORD_MIN_LENGTH", 0))
PASSWORD_MAX_LENGTH: int = int(os.environ.get("PASSWORD_MAX_LENGTH", 0))
PASSWORD_ALLOWED_CHARACTERS: str = string.printable

AUTHENTICATION_HEADER: str = os.environ.get("AUTHENTICATION_HEADER", "")
AUTHENTICATION_HEADER_PREFIX: str = os.environ.get("AUTHENTICATION_HEADER_PREFIX", "")

CONFIRM_EMAIL_CODE_DURATION: int = int(
    os.environ.get("CONFIRM_EMAIL_CODE_DURATION", 0)
)  # seconds
CONFIRM_EMAIL_CHECK_DELAY: int = int(
    os.environ.get("CONFIRM_EMAIL_CHECK_DELAY", 0)
)  # seconds

RESET_PASSWORD_CODE_DURATION: int = int(
    os.environ.get("RESET_PASSWORD_CODE_DURATION", 0)
)  # seconds

CONFIRMATION_CODE_LENGTH: int = int(os.environ.get("CONFIRMATION_CODE_LENGTH", 0))
CONFIRMATION_CODE_CHARACTERS: str = string.digits

AUTH_GRPC_SERVER_HOST: str = os.environ.get("AUTH_GRPC_SERVER_HOST", "")
AUTH_GRPC_SERVER_PORT: str = os.environ.get("AUTH_GRPC_SERVER_PORT", "")

PUBLISHER_GRPC_HOST: str = os.environ.get("PUBLISHER_GRPC_HOST", "")
PUBLISHER_GRPC_PORT: str = os.environ.get("PUBLISHER_GRPC_PORT", "")

APP_NAME: str = os.environ.get("AUTH_APP_NAME", "")
PORT: str = os.environ.get("AUTH_PORT", "")
APP_VERSION: str = os.environ.get("APP_VERSION", "")
ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "")
DEBUG: bool = bool(int(os.environ.get("DEBUG", 0)))

LOGGING_MAX_BYTES: int = int(os.environ.get("LOGGING_MAX_BYTES", 0))
LOGGING_BACKUP_COUNT: int = int(os.environ.get("LOGGING_BACKUP_COUNT", 0))
LOGGING_LOGGERS: List[str] = os.environ.get("LOGGING_AUTH_LOGGERS").split(",")
LOGGING_SENSITIVE_FIELDS: List[str] = os.environ.get(
    "LOGGING_AUTH_SENSITIVE_FIELDS"
).split(",")
LOG_PATH: str = os.environ.get("LOGGING_AUTH_PATH", "")
