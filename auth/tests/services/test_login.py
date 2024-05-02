from unittest import mock

import pytest

from config.di import get_di_test_container
from services.login import LoginUser
from schemas import LoginSchema, JWTTokensSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom401Exception, Custom404Exception


container = get_di_test_container()


class TestLoginUser(ServiceTestMixin):
    def setup_method(self):
        self.entry = LoginSchema(login=self.user.email, password=self.user.password)
        self.tokens = JWTTokensSchema(access="access", refresh="refresh")

        self.create_jwt_tokens = mock.Mock(return_value=self.tokens)
        self.check_password = mock.Mock(return_value=True)

        self.repo = mock.Mock()
        self.repo.get_by_login.return_value = self.user

        self.context = container.login_user.override(
            LoginUser(
                create_jwt_tokens=self.create_jwt_tokens,
                check_password=self.check_password,
                repo=self.repo,
            )
        )

    def test_user_not_found(self):
        self.repo.get_by_login.return_value = None
        with self.context, pytest.raises(Custom404Exception):
            container.login_user()(self.entry)

            self.check_password.assert_not_called()
            self.create_jwt_tokens.assert_not_called()

    def test_wrong_password(self):
        self.check_password.return_value = False
        with self.context, pytest.raises(Custom401Exception):
            container.login_user()(self.entry)

            self.check_password.assert_called_once_with(
                self.entry.password, self.user.password
            )
            self.create_jwt_tokens.assert_not_called()

    def test_login(self):
        with self.context:
            tokens = container.login_user()(self.entry)

            assert isinstance(tokens, JWTTokensSchema)
            assert tokens == self.tokens
            self.check_password.assert_called_once_with(
                self.entry.password, self.user.password
            )
            self.create_jwt_tokens.assert_called_once_with(self.user)
