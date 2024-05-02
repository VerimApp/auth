from unittest import mock
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest
from pytest_mock import MockerFixture

from config import settings
from config.di import get_di_test_container
from services.codes import CheckCode
from services.codes.types import CodeTypeEnum
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception


container = get_di_test_container()


class TestCheckCode(ServiceTestMixin):
    def setup_method(self):
        self.now = datetime(10, 10, 10)
        self.last_code = SimpleNamespace(
            **{"id": 1, "created_at": self.now, "code": "1111"}
        )

        self.repo = mock.Mock()
        self.repo.get_last.return_value = self.last_code

        self.context = container.check_code.override(CheckCode(repo=self.repo))

    def test_check(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        with self.context:
            is_valid = container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code=self.last_code.code,
                raise_exception=False,
            )

            assert is_valid
            self.repo.get_last.assert_called_once_with(
                self.user.id, CodeTypeEnum.EMAIL_CONFIRM
            )
            get_current_time.assert_called_once_with()

    def test_check_fail_time(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        self.last_code.created_at = self.last_code.created_at - timedelta(
            seconds=settings.CONFIRM_EMAIL_CODE_DURATION + 1
        )
        with self.context:
            is_valid = container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code=self.last_code.code,
                raise_exception=False,
            )

            assert not is_valid
            self.repo.get_last.assert_called_once_with(
                self.user.id, CodeTypeEnum.EMAIL_CONFIRM
            )
            get_current_time.assert_called_once_with()

    def test_check_fail_time_raise_exc(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        self.last_code.created_at = self.last_code.created_at - timedelta(
            seconds=settings.CONFIRM_EMAIL_CODE_DURATION + 1
        )
        with self.context, pytest.raises(Custom400Exception):
            container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code=self.last_code.code,
                raise_exception=True,
            )

    def test_check_fail_code(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        with self.context:
            is_valid = container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code="9999",
                raise_exception=False,
            )

            assert not is_valid
            self.repo.get_last.assert_called_once_with(
                self.user.id, CodeTypeEnum.EMAIL_CONFIRM
            )
            get_current_time.assert_called_once_with()

    def test_check_fail_code_raise_exc(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        with self.context, pytest.raises(Custom400Exception):
            container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code="9999",
                raise_exception=True,
            )

    def test_check_no_last(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        self.repo.get_last.return_value = None
        with self.context:
            is_valid = container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code=self.last_code.code,
                raise_exception=False,
            )

            assert not is_valid
            self.repo.get_last.assert_called_once_with(
                self.user.id, CodeTypeEnum.EMAIL_CONFIRM
            )
            get_current_time.assert_not_called()

    def test_check_no_last_raise_exc(self, mocker: MockerFixture):
        get_current_time = mocker.patch("services.codes.check.get_current_time")
        get_current_time.return_value = self.now
        self.repo.get_last.return_value = None
        with self.context, pytest.raises(Custom400Exception):
            container.check_code()(
                user=self.user,
                type=CodeTypeEnum.EMAIL_CONFIRM,
                code=self.last_code.code,
                raise_exception=True,
            )

            self.repo.get_last.assert_called_once_with(
                self.user.id, CodeTypeEnum.EMAIL_CONFIRM
            )
            get_current_time.assert_not_called()
