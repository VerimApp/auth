from unittest import mock
from datetime import datetime, timedelta

import pytest
from pytest_mock import MockerFixture
from jwt.exceptions import PyJWTError

from config import settings
from config.di import get_di_test_container
from services.authenticate import Authenticate
from utils.test import ServiceTestMixin
from utils.exceptions import Custom401Exception, Custom403Exception


container = get_di_test_container()


class TestAuthenticateByToken(ServiceTestMixin):
    def setup_method(self):
        self.now = datetime(10, 10, 10)
        self.token = "token"
        self.payload = {
            "user": self.user.id,
            "exp": self.now.timestamp(),
            "created_at": (
                self.now - timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME)
            ),
        }

        self.repo = mock.Mock()
        self.repo.get_by_id.return_value = self.user

        self.context = container.authenticate.override(Authenticate(repo=self.repo))

    def test_access_jwt_error(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.exceptions.PyJWTError = PyJWTError
        jwt.decode.side_effect = PyJWTError
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=True)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.ACCESS_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_not_called()
            timestamp_to_datetime.assert_not_called()

    def test_access_payload_error(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        self.payload.pop("created_at")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=True)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.ACCESS_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_not_called()
            timestamp_to_datetime.assert_not_called()

    def test_access_user_not_found(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )

        self.repo.get_by_id.return_value = None
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=True)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.ACCESS_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_not_called()

    def test_access_token_revoked(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        timestamp_to_datetime.return_value = self.now - timedelta(seconds=1)

        self.user.tokens_revoked_at = self.now
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=True)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.ACCESS_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_called_once_with(self.payload["created_at"])
        self.user.tokens_revoked_at = None

    def test_access_user_not_active(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )

        self.user.is_active = False
        with self.context, pytest.raises(Custom403Exception):
            container.authenticate()(self.token, access=True)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.ACCESS_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_not_called()
        self.user.is_active = True

    def test_refresh_jwt_error(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.exceptions.PyJWTError = PyJWTError
        jwt.decode.side_effect = PyJWTError
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=False)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_not_called()
            timestamp_to_datetime.assert_not_called()

    def test_refresh_payload_error(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        self.payload.pop("created_at")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=False)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_not_called()
            timestamp_to_datetime.assert_not_called()

    def test_refresh_user_not_found(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )

        self.repo.get_by_id.return_value = None
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=False)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_not_called()

    def test_refresh_token_revoked(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        timestamp_to_datetime.return_value = self.now - timedelta(seconds=1)

        self.user.tokens_revoked_at = self.now
        with self.context, pytest.raises(Custom401Exception):
            container.authenticate()(self.token, access=False)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_called_once_with(self.payload["created_at"])
        self.user.tokens_revoked_at = None

    def test_refresh_user_not_active(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )

        self.user.is_active = False
        with self.context, pytest.raises(Custom403Exception):
            container.authenticate()(self.token, access=False)

            jwt.decode.assert_called_once_with(
                self.token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_not_called()
        self.user.is_active = True

    def test_authenticate_by_access(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        with self.context:
            user = container.authenticate()(self.token, access=True)

            assert user == self.user
            jwt.decode.assert_called_once_with(
                self.token,
                settings.ACCESS_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_not_called()

    def test_authenticate_by_refresh(self, mocker: MockerFixture):
        jwt = mocker.patch("services.authenticate.jwt")
        jwt.decode.return_value = self.payload
        timestamp_to_datetime = mocker.patch(
            "services.authenticate.timestamp_to_datetime"
        )
        with self.context:
            user = container.authenticate()(self.token, access=False)

            assert user == self.user
            jwt.decode.assert_called_once_with(
                self.token,
                settings.REFRESH_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            self.repo.get_by_id.assert_called_once_with(self.payload["user"])
            timestamp_to_datetime.assert_not_called()
