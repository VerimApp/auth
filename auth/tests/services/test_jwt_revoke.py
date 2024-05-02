from unittest import mock
from datetime import datetime

from pytest_mock import MockerFixture

from config.di import get_di_test_container
from services.jwt import RevokeJWTTokens
from utils.test import ServiceTestMixin


container = get_di_test_container()


class TestRevokeJWTTokens(ServiceTestMixin):
    def setup_method(self):
        self.now = datetime(10, 10, 10)

        self.repo = mock.Mock()

        self.context = container.revoke_jwt_tokens.override(
            RevokeJWTTokens(repo=self.repo)
        )

    def test_revoke(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.jwt.revoke.get_current_time")
        get_current_time.return_value = self.now
        with self.context:
            container.revoke_jwt_tokens()(self.user)

            self.repo.update.assert_called_once_with(
                self.user, {"tokens_revoked_at": self.now}
            )
