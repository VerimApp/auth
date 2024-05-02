from unittest import mock

import pytest

from config.di import get_di_test_container
from services.registration import ConfirmRegistration
from services.codes.types import CodeTypeEnum
from schemas import ConfirmRegistrationSchema, JWTTokensSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception, Custom404Exception


container = get_di_test_container()


class TestConfirmRegistration(ServiceTestMixin):
    def setup_method(self):
        self.entry = ConfirmRegistrationSchema(email=self.user.email, code="1111")

        self.tokens = JWTTokensSchema(access="access", refresh="refresh")

        self.create_jwt_tokens = mock.Mock(return_value=self.tokens)
        self.check_code = mock.Mock(return_value=True)

        self.repo = mock.Mock()
        self.repo.get_by_email.return_value = self.user

        self.context = container.confirm_registration.override(
            ConfirmRegistration(
                create_jwt_tokens=self.create_jwt_tokens,
                check_code=self.check_code,
                repo=self.repo,
            )
        )

        self.user.email_confirmed = False

    def teardown_class(self):
        self.user.email_confirmed = True

    def test_user_not_found(self):
        self.repo.get_by_email.return_value = None
        with self.context, pytest.raises(Custom404Exception):
            container.confirm_registration()(self.entry)

            self.create_jwt_tokens.assert_not_called()
            self.check_code.assert_not_called()
            self.repo.update.assert_not_called()

    def test_email_already_confirmed(self):
        self.user.email_confirmed = True
        with self.context, pytest.raises(Custom400Exception):
            container.confirm_registration()(self.entry)

            self.create_jwt_tokens.assert_not_called()
            self.check_code.assert_not_called()
            self.repo.update.assert_not_called()

    def test_wrong_code(self):
        self.check_code.side_effect = Custom400Exception
        with self.context, pytest.raises(Custom400Exception):
            container.confirm_registration()(self.entry)

            self.create_jwt_tokens.assert_not_called()
            self.check_code.assert_called_once_with(
                user=self.user, type=CodeTypeEnum.EMAIL_CONFIRM, code=self.entry.code
            )
            self.repo.update.assert_not_called()

    def test_confirm(self):
        with self.context:
            tokens = container.confirm_registration()(self.entry)

            assert isinstance(tokens, JWTTokensSchema)
            assert tokens == self.tokens
            self.create_jwt_tokens.assert_called_once_with(self.user)
            self.check_code.assert_called_once_with(
                user=self.user, type=CodeTypeEnum.EMAIL_CONFIRM, code=self.entry.code
            )
            self.repo.update.assert_called_once_with(
                self.user, values={"email_confirmed": True}
            )
