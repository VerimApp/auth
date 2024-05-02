from unittest import mock
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from config import settings
from config.di import get_di_test_container
from services.codes import CreateCode
from services.entries import CreateCodeEntry, SendCodeEntry
from services.codes.types import CodeTypeEnum
from schemas import CodeSentSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception


container = get_di_test_container()


class TestCreateCode(ServiceTestMixin):
    def setup_method(self):
        self.now = datetime(10, 10, 10)
        self.code = "1111"
        self.last_code = SimpleNamespace(
            **{
                "id": 1,
                "created_at": self.now,
                "code": self.code,
                "type": CodeTypeEnum.EMAIL_CONFIRM,
            }
        )
        self.new_code = SimpleNamespace(
            **{
                "id": 2,
                "created_at": self.now
                + timedelta(seconds=settings.CONFIRM_EMAIL_CODE_DURATION),
                "code": self.code,
                "type": CodeTypeEnum.EMAIL_CONFIRM,
            }
        )

        self.code_sent = CodeSentSchema(email=self.user.email, message="message")

        self.send_code = mock.Mock()
        self.send_code.return_value = self.code_sent

        self.repo = mock.Mock()
        self.repo.get_last.return_value = self.last_code
        self.repo.create.return_value = self.new_code

        self.context = container.create_code.override(
            CreateCode(send_code=self.send_code, repo=self.repo)
        )

    def test_create_no_last_code(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.create.get_current_time")
        get_current_time.return_value = self.now
        get_random_string = mocker.patch("services.codes.create.get_random_string")
        get_random_string.return_value = self.code
        self.repo.get_last.return_value = None
        with self.context:
            code = container.create_code()(
                user=self.user, type=CodeTypeEnum.EMAIL_CONFIRM, send=True
            )

            assert isinstance(code, CodeSentSchema)
            assert code == self.code_sent
            get_current_time.assert_not_called()
            get_random_string.assert_called_once_with(
                length=settings.CONFIRMATION_CODE_LENGTH,
                allowed_characters=settings.CONFIRMATION_CODE_CHARACTERS,
            )
            self.repo.create.assert_called_once_with(
                entry=CreateCodeEntry(
                    user_id=self.user.id,
                    code=self.code,
                    type=CodeTypeEnum.EMAIL_CONFIRM,
                )
            )
            self.send_code.assert_called_once_with(
                entry=SendCodeEntry(
                    email=self.user.email,
                    code=self.code,
                    type=CodeTypeEnum.EMAIL_CONFIRM,
                )
            )

    def test_create_last_code_not_active(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.create.get_current_time")
        get_current_time.return_value = self.now
        get_random_string = mocker.patch("services.codes.create.get_random_string")
        get_random_string.return_value = self.code
        self.last_code.created_at = self.last_code.created_at - timedelta(
            seconds=settings.CONFIRM_EMAIL_CODE_DURATION + 1
        )
        with self.context:
            code = container.create_code()(
                user=self.user, type=CodeTypeEnum.EMAIL_CONFIRM, send=True
            )

            assert isinstance(code, CodeSentSchema)
            assert code == self.code_sent
            get_current_time.assert_called_once_with()
            get_random_string.assert_called_once_with(
                length=settings.CONFIRMATION_CODE_LENGTH,
                allowed_characters=settings.CONFIRMATION_CODE_CHARACTERS,
            )
            self.repo.create.assert_called_once_with(
                entry=CreateCodeEntry(
                    user_id=self.user.id,
                    code=self.code,
                    type=CodeTypeEnum.EMAIL_CONFIRM,
                )
            )
            self.send_code.assert_called_once_with(
                entry=SendCodeEntry(
                    email=self.user.email,
                    code=self.code,
                    type=CodeTypeEnum.EMAIL_CONFIRM,
                )
            )

    def test_create_active_last_code(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.create.get_current_time")
        get_current_time.return_value = self.now
        get_random_string = mocker.patch("services.codes.create.get_random_string")
        get_random_string.return_value = self.code
        with self.context, pytest.raises(Custom400Exception):
            container.create_code()(
                user=self.user, type=CodeTypeEnum.EMAIL_CONFIRM, send=True
            )

            get_current_time.assert_called_once_with()
            get_random_string.assert_called_once_with(
                length=settings.CONFIRMATION_CODE_LENGTH,
                allowed_characters=settings.CONFIRMATION_CODE_CHARACTERS,
            )
            self.repo.create.assert_not_called()
            self.send_code.assert_not_called()

    def test_create_no_send(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.create.get_current_time")
        get_current_time.return_value = self.now
        get_random_string = mocker.patch("services.codes.create.get_random_string")
        get_random_string.return_value = self.code
        self.repo.get_last.return_value = None
        with self.context:
            code = container.create_code()(
                user=self.user, type=CodeTypeEnum.EMAIL_CONFIRM, send=False
            )

            assert isinstance(code, str)
            assert code == self.code
            get_current_time.assert_not_called()
            get_random_string.assert_called_once_with(
                length=settings.CONFIRMATION_CODE_LENGTH,
                allowed_characters=settings.CONFIRMATION_CODE_CHARACTERS,
            )
            self.repo.create.assert_called_once_with(
                entry=CreateCodeEntry(
                    user_id=self.user.id,
                    code=self.code,
                    type=CodeTypeEnum.EMAIL_CONFIRM,
                )
            )
            self.send_code.assert_not_called()
