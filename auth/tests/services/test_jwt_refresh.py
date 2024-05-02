from unittest import mock

from pytest_mock import MockerFixture

from config.di import get_di_test_container
from services.jwt import RefreshJWTTokens
from schemas import JWTTokensSchema, RefreshTokensSchema
from utils.test import ServiceTestMixin


container = get_di_test_container()


class TestRefreshJWTTokens(ServiceTestMixin):
    def setup_method(self):
        self.entry = RefreshTokensSchema(refresh="refresh")

        self.tokens = JWTTokensSchema(
            access="access",
            refresh="refresh",
        )

        self.authenticate = mock.Mock(return_value=self.user)

        self.create_jwt_tokens = mock.Mock()
        self.create_jwt_tokens.return_value = self.tokens

        self.context = container.refresh_jwt_tokens.override(
            RefreshJWTTokens(
                authenticate=self.authenticate, create_jwt_tokens=self.create_jwt_tokens
            )
        )

    def test_refresh(self):
        with self.context:
            tokens = container.refresh_jwt_tokens()(self.entry)

            assert isinstance(tokens, JWTTokensSchema)
            assert tokens == self.tokens
            self.authenticate.assert_called_once_with(self.entry.refresh, access=False)
            self.create_jwt_tokens.assert_called_once_with(user=self.user)
