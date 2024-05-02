from unittest import mock

import pytest

from config.di import get_di_test_container
from services.password import ChangePassword
from schemas import ChangePasswordSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception


container = get_di_test_container()


class TestChangePassword(ServiceTestMixin):
    def setup_method(self):
        self.entry = ChangePasswordSchema(
            current_password="current_password",
            new_password="new_password",
            re_new_password="new_password",
        )

        self.check_password = mock.Mock(return_value=True)

        self.validate_password = mock.Mock()

        self.hash_password = mock.Mock(return_value="hashed")

        self.revoke_jwt_tokens = mock.Mock()

        self.repo = mock.Mock()
        self.repo.get_by_id.return_value = self.user

        self.context = container.change_password.override(
            ChangePassword(
                check_password=self.check_password,
                validate_password=self.validate_password,
                hash_password=self.hash_password,
                revoke_jwt_tokens=self.revoke_jwt_tokens,
                repo=self.repo,
            )
        )

    def test_change_wrong_current_password(self):
        self.check_password.return_value = False
        with self.context, pytest.raises(Custom400Exception):
            container.change_password()(self.user.id, self.entry)

            self.check_password.assert_called_once_with(
                self.entry.current_password, self.user.password
            )
            self.validate_password.assert_not_called()
            self.repo.update.assert_not_called()
            self.revoke_jwt_tokens.assert_not_called()
            self.hash_password.assert_not_called()

    def test_change_password_mismatch(self):
        self.entry.re_new_password = "re_new_password"
        with self.context, pytest.raises(Custom400Exception):
            container.change_password()(self.user.id, self.entry)

            self.check_password.assert_called_once_with(
                self.entry.current_password, self.user.password
            )
            self.validate_password.assert_not_called()
            self.repo.update.assert_not_called()
            self.revoke_jwt_tokens.assert_not_called()
            self.hash_password.assert_not_called()

    def test_change_same_password(self):
        self.entry.new_password = self.entry.current_password
        self.entry.re_new_password = self.entry.current_password
        with self.context, pytest.raises(Custom400Exception):
            container.change_password()(self.user.id, self.entry)

            self.check_password.assert_called_once_with(
                self.entry.current_password, self.user.password
            )
            self.validate_password.assert_not_called()
            self.repo.update.assert_not_called()
            self.revoke_jwt_tokens.assert_not_called()
            self.hash_password.assert_not_called()

    def test_change_password_not_valid(self):
        self.validate_password.side_effect = Custom400Exception
        with self.context, pytest.raises(Custom400Exception):
            container.change_password()(self.user.id, self.entry)

            self.check_password.assert_called_once_with(
                self.entry.current_password, self.user.password
            )
            self.validate_password.assert_called_once_with(
                self.entry.new_password, raise_exception=True
            )
            self.repo.update.assert_not_called()
            self.revoke_jwt_tokens.assert_not_called()
            self.hash_password.assert_not_called()

    def test_change(self):
        with self.context:
            container.change_password()(self.user.id, self.entry)

            self.check_password.assert_called_once_with(
                self.entry.current_password, self.user.password
            )
            self.validate_password.assert_called_once_with(
                self.entry.new_password, raise_exception=True
            )
            self.repo.update.assert_called_once_with(self.user, {"password": "hashed"})
            self.revoke_jwt_tokens.assert_called_once_with(self.user)
            self.hash_password.assert_called_once_with(self.entry.new_password)
