from unittest import mock

import pytest

from config.di import get_di_test_container
from services.registration import RepeatRegistrationCode
from services.codes.types import CodeTypeEnum
from schemas import RepeatRegistrationCodeSchema, CodeSentSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception, Custom404Exception


container = get_di_test_container()


class TestRepeatRegistrationCode(ServiceTestMixin):
    def setup_method(self):
        self.entry = RepeatRegistrationCodeSchema(email=self.user.email)
        self.code_sent = CodeSentSchema(email=self.user.email, message="message")

        self.create_code = mock.Mock(return_value=self.code_sent)

        self.repo = mock.Mock()
        self.repo.get_by_email.return_value = self.user

        self.context = container.repeat_registration_code.override(
            RepeatRegistrationCode(create_code=self.create_code, repo=self.repo)
        )

    def test_user_not_found(self):
        self.repo.get_by_email.return_value = None
        with self.context, pytest.raises(Custom404Exception):
            container.repeat_registration_code()(self.entry)

            self.create_code.assert_not_called()

    def test_email_already_confirmed(self):
        self.user.email_confirmed = True
        with self.context, pytest.raises(Custom400Exception):
            container.repeat_registration_code()(self.entry)

            self.create_code.assert_not_called()

        self.user.email_confirmed = False

    def test_repeat(self):
        with self.context:
            code_sent = container.repeat_registration_code()(self.entry)

            assert isinstance(code_sent, CodeSentSchema)
            assert code_sent == self.code_sent
            self.create_code.assert_called_once_with(
                self.user, CodeTypeEnum.EMAIL_CONFIRM, send=True
            )
