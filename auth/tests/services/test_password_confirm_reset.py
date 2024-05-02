from unittest import mock

import pytest

from config.di import get_di_test_container
from services.password import ConfirmResetPassword
from services.codes.types import CodeTypeEnum
from schemas import ResetPasswordConfirmSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception, Custom404Exception


container = get_di_test_container()


class TestConfirmResetPassword(ServiceTestMixin):
    def setup_method(self):
        self.entry = ResetPasswordConfirmSchema(
            email=self.user.email,
            code="1111",
            new_password="new_password",
            re_new_password="new_password",
        )

        self.check_code = mock.Mock(return_value=True)
        self.validate_password = mock.Mock(return_value=True)
        self.hash_password = mock.Mock(return_value="hashed")
        self.check_password = mock.Mock(return_value=False)

        self.repo = mock.Mock()
        self.repo.get_by_email.return_value = self.user

        self.context = container.confirm_reset_password.override(
            ConfirmResetPassword(
                check_code=self.check_code,
                validate_password=self.validate_password,
                hash_password=self.hash_password,
                check_password=self.check_password,
                repo=self.repo,
            )
        )

    def test_user_not_found(self):
        self.repo.get_by_email.return_value = None
        with self.context, pytest.raises(Custom404Exception):
            container.confirm_reset_password()(self.entry)

            self.check_code.assert_not_called()
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.check_password.assert_not_called()
            self.repo.update.assert_not_called()

    def test_wrong_code(self):
        self.check_code.side_effect = Custom400Exception
        with self.context, pytest.raises(Custom400Exception):
            container.confirm_reset_password()(self.entry)

            self.check_code.assert_called_once_with(
                self.user, CodeTypeEnum.RESET_PASSWORD, self.entry.code
            )
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.check_password.assert_not_called()
            self.repo.update.assert_not_called()

    def test_password_mismatch(self):
        self.entry.re_new_password = "re_new_password"
        with self.context, pytest.raises(Custom400Exception):
            container.confirm_reset_password()(self.entry)

            self.check_code.assert_called_once_with(
                self.user, CodeTypeEnum.RESET_PASSWORD, self.entry.code
            )
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.check_password.assert_not_called()
            self.repo.update.assert_not_called()

    def test_password_same(self):
        self.check_password.return_value = True
        with self.context, pytest.raises(Custom400Exception):
            container.confirm_reset_password()(self.entry)

            self.check_code.assert_called_once_with(
                self.user, CodeTypeEnum.RESET_PASSWORD, self.entry.code
            )
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.check_password.assert_called_once_with(
                self.entry.new_password, self.user.password
            )
            self.repo.update.assert_not_called()

    def test_password_not_valid(self):
        self.validate_password.side_effect = Custom400Exception
        with self.context, pytest.raises(Custom400Exception):
            container.confirm_reset_password()(self.entry)

            self.check_code.assert_called_once_with(
                self.user, CodeTypeEnum.RESET_PASSWORD, self.entry.code
            )
            self.validate_password.assert_called_once_with(
                self.entry.new_password, raise_exception=True
            )
            self.hash_password.assert_not_called()
            self.check_password.assert_called_once_with(
                self.entry.new_password, self.user.password
            )
            self.repo.update.assert_not_called()

    def test_reset(self):
        with self.context:
            container.confirm_reset_password()(self.entry)

            self.check_code.assert_called_once_with(
                self.user, CodeTypeEnum.RESET_PASSWORD, self.entry.code
            )
            self.validate_password.assert_called_once_with(
                self.entry.new_password, raise_exception=True
            )
            self.hash_password.assert_called_once_with(self.entry.new_password)
            self.check_password.assert_called_once_with(
                self.entry.new_password, self.user.password
            )
            self.repo.update.assert_called_once_with(
                user=self.user, values={"password": "hashed"}
            )
