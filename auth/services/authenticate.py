import logging
from abc import ABC, abstractmethod
from typing import Dict

import jwt

from config import settings
from config.i18n import _
from services.repo import IUserRepo
from services.entries import JWTPayload
from utils.time import timestamp_to_datetime
from utils.types import UserType
from utils.exceptions import Custom401Exception, Custom403Exception


logger = logging.getLogger("auth")


class IAuthenticate(ABC):
    @abstractmethod
    def __call__(self, token: str | bytes, *, access: bool = True) -> UserType: ...


class Authenticate(IAuthenticate):
    def __init__(self, repo: IUserRepo):
        self.repo = repo

    def __call__(self, token: str | bytes, *, access: bool = True) -> UserType:
        payload = self._decode_payload(token, access)
        payload = self._payload_to_dataclass(payload)
        user = self._get_user(payload.user)
        self._check_tokens_revoked(user, payload)
        self._check_user_active(user)
        return user

    def _decode_payload(self, token: str | bytes, access: bool) -> Dict:
        try:
            return jwt.decode(
                token,
                settings.ACCESS_SECRET_KEY if access else settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.PyJWTError:
            raise Custom401Exception(_("Token is not correct."))

    def _payload_to_dataclass(self, payload: Dict) -> JWTPayload:
        try:
            return JWTPayload(**payload)
        except TypeError as e:
            logger.error(
                f"JWT payload has bad structure - {str(e)}",
                extra={"payload": payload},
                exc_info=e,
            )
            raise Custom401Exception(_("Token is not correct."))

    def _get_user(self, user_id: int) -> UserType:
        user: UserType = self.repo.get_by_id(user_id)
        if not user:
            raise Custom401Exception(_("Token is not correct."))
        return user

    def _check_tokens_revoked(self, user: UserType, payload: JWTPayload) -> None:
        if user.tokens_revoked_at and user.tokens_revoked_at > timestamp_to_datetime(
            payload.created_at
        ):
            raise Custom401Exception(_("Token is not correct."))

    def _check_user_active(self, user: UserType) -> None:
        if not user.is_active:
            raise Custom403Exception(_("User is not active."))
