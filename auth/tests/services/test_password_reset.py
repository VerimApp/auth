from unittest import mock

import pytest

from config.di import get_di_test_container
from services.password import ResetPassword
from services.codes.types import CodeTypeEnum
from schemas import ResetPasswordSchema, CodeSentSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom404Exception


container = get_di_test_container()


class TestResetPassword(ServiceTestMixin):
    def setup_method(self):
        self.entry = ResetPasswordSchema(email=self.user.email)

        self.code_sent = CodeSentSchema(email=self.user.email, message="message")

        self.create_code = mock.Mock(return_value=self.code_sent)

        self.repo = mock.Mock()
        self.repo.get_by_email.return_value = self.user

        self.context = container.reset_password.override(
            ResetPassword(create_code=self.create_code, repo=self.repo)
        )

    def test_user_not_found(self):
        self.repo.get_by_email.return_value = None
        with self.context, pytest.raises(Custom404Exception):
            container.reset_password()(self.entry)

            self.create_code.assert_not_called()

    def test_reset(self):
        with self.context:
            code_sent = container.reset_password()(self.entry)

            assert isinstance(code_sent, CodeSentSchema)
            assert code_sent == self.code_sent
            self.create_code.assert_called_once_with(
                self.user, CodeTypeEnum.RESET_PASSWORD, send=True
            )
