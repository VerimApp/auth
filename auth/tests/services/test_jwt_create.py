from unittest import mock
from datetime import datetime, timedelta

from pytest_mock import MockerFixture

from config import settings
from config.di import get_di_test_container
from services.jwt import CreateJWTTokens
from schemas import JWTTokensSchema
from utils.test import ServiceTestMixin


container = get_di_test_container()


class TestCreateJWTTokens(ServiceTestMixin):
    def setup_method(self):
        self.now = datetime(10, 10, 10)

        self.context = container.create_jwt_tokens.override(CreateJWTTokens())

    def test_create(self, mocker: MockerFixture):
        jwt = mocker.patch("services.jwt.create.jwt")
        jwt.encode.return_value = "encoded"
        get_current_time = mocker.patch("services.jwt.create.get_current_time")
        get_current_time.return_value = self.now
        with self.context:
            tokens = container.create_jwt_tokens()(self.user)

            assert isinstance(tokens, JWTTokensSchema)
            assert tokens.access == "encoded"
            assert tokens.refresh == "encoded"
            assert get_current_time.call_count == 2
            assert jwt.encode.call_args_list == [
                mock.call(
                    payload={
                        "user": self.user.id,
                        "exp": (
                            self.now + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME)
                        ).timestamp(),
                        "created_at": self.now.timestamp(),
                    },
                    key=settings.ACCESS_SECRET_KEY,
                    algorithm=settings.JWT_ALGORITHM,
                ),
                mock.call(
                    payload={
                        "user": self.user.id,
                        "exp": (
                            self.now
                            + timedelta(minutes=settings.REFRESH_TOKEN_LIFETIME)
                        ).timestamp(),
                        "created_at": self.now.timestamp(),
                    },
                    key=settings.REFRESH_SECRET_KEY,
                    algorithm=settings.JWT_ALGORITHM,
                ),
            ]
