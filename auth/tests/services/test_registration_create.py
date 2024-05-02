from unittest import mock
from datetime import datetime

import pytest
from pytest_mock import MockerFixture

from config import settings
from config.di import get_di_test_container
from services.registration import RegisterUser
from services.codes.types import CodeTypeEnum
from schemas import RegistrationSchema, CodeSentSchema
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception


container = get_di_test_container()


class TestRegisterUser(ServiceTestMixin):
    def setup_method(self):
        self.now = datetime(10, 10, 10)
        self.entry = RegistrationSchema(
            email=self.user.email,
            username=self.user.username,
            password="password",
            re_password="password",
        )
        self.code_sent = CodeSentSchema(email=self.user.email, message="message")

        self.create_code = mock.Mock(return_value=self.code_sent)
        self.validate_username = mock.Mock(return_value=True)
        self.validate_password = mock.Mock(return_value=True)
        self.hash_password = mock.Mock(return_value="hashed")
        self.celery_app = mock.Mock()

        self.repo = mock.Mock()
        self.repo.email_exists.return_value = False
        self.repo.username_exists.return_value = False
        self.repo.create.return_value = self.user

        self.context = container.register_user.override(
            RegisterUser(
                create_code=self.create_code,
                validate_username=self.validate_username,
                validate_password=self.validate_password,
                hash_password=self.hash_password,
                repo=self.repo,
                celery_app=self.celery_app,
            )
        )

    def test_email_exists(self, mocker: MockerFixture):
        get_current_time_with_delta = mocker.patch(
            "services.registration.create.get_current_time_with_delta"
        )
        get_current_time_with_delta.return_value = self.now
        self.repo.email_exists.return_value = True
        with self.context, pytest.raises(Custom400Exception):
            container.register_user()(self.entry)

            self.create_code.assert_not_called()
            self.validate_username.assert_not_called()
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.repo.create.assert_not_called()
            self.celery_app.send_task.assert_not_called()
            get_current_time_with_delta.assert_not_called()

    def test_username_exists(self, mocker: MockerFixture):
        get_current_time_with_delta = mocker.patch(
            "services.registration.create.get_current_time_with_delta"
        )
        get_current_time_with_delta.return_value = self.now
        self.repo.username_exists.return_value = True
        with self.context, pytest.raises(Custom400Exception):
            container.register_user()(self.entry)

            self.create_code.assert_not_called()
            self.validate_username.assert_not_called()
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.repo.create.assert_not_called()
            self.celery_app.send_task.assert_not_called()
            get_current_time_with_delta.assert_not_called()

    def test_username_not_valid(self, mocker: MockerFixture):
        get_current_time_with_delta = mocker.patch(
            "services.registration.create.get_current_time_with_delta"
        )
        get_current_time_with_delta.return_value = self.now
        self.validate_username.side_effect = Custom400Exception
        with self.context, pytest.raises(Custom400Exception):
            container.register_user()(self.entry)

            self.create_code.assert_not_called()
            self.validate_username.assert_called_once_with(
                self.entry.username, raise_exception=True
            )
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.repo.create.assert_not_called()
            self.celery_app.send_task.assert_not_called()
            get_current_time_with_delta.assert_not_called()

    def test_password_mismatch(self, mocker: MockerFixture):
        get_current_time_with_delta = mocker.patch(
            "services.registration.create.get_current_time_with_delta"
        )
        get_current_time_with_delta.return_value = self.now
        self.entry.re_password = "re_password"
        with self.context, pytest.raises(Custom400Exception):
            container.register_user()(self.entry)

            self.create_code.assert_not_called()
            self.validate_username.assert_called_once_with(
                self.entry.username, raise_exception=True
            )
            self.validate_password.assert_not_called()
            self.hash_password.assert_not_called()
            self.repo.create.assert_not_called()
            self.celery_app.send_task.assert_not_called()
            get_current_time_with_delta.assert_not_called()

    def test_password_not_valid(self, mocker: MockerFixture):
        get_current_time_with_delta = mocker.patch(
            "services.registration.create.get_current_time_with_delta"
        )
        get_current_time_with_delta.return_value = self.now
        self.validate_password.side_effect = Custom400Exception
        with self.context, pytest.raises(Custom400Exception):
            container.register_user()(self.entry)

            self.create_code.assert_not_called()
            self.validate_username.assert_called_once_with(
                self.entry.username, raise_exception=True
            )
            self.validate_password.assert_called_once_with(
                self.entry.password, raise_exception=True
            )
            self.hash_password.assert_not_called()
            self.repo.create.assert_not_called()
            self.celery_app.send_task.assert_not_called()
            get_current_time_with_delta.assert_not_called()

    def test_register(self, mocker: MockerFixture):
        get_current_time_with_delta = mocker.patch(
            "services.registration.create.get_current_time_with_delta"
        )
        get_current_time_with_delta.return_value = self.now
        with self.context:
            container.register_user()(self.entry)

            self.create_code.assert_called_once_with(
                self.user, CodeTypeEnum.EMAIL_CONFIRM, send=True
            )
            self.validate_username.assert_called_once_with(
                self.entry.username, raise_exception=True
            )
            self.validate_password.assert_called_once_with(
                self.entry.re_password, raise_exception=True
            )
            self.hash_password.assert_called_once_with(self.entry.re_password)
            self.repo.create.assert_called_once_with(self.entry)
            self.celery_app.send_task.assert_called_once_with(
                "config.celery.check_email_confirmed",
                args=(self.user.id,),
                eta=self.now,
            )
            get_current_time_with_delta.assert_called_once_with(
                seconds=settings.CONFIRM_EMAIL_CHECK_DELAY
            )
