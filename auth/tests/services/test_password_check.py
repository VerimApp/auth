from pytest_mock import MockerFixture

from config.di import get_di_test_container
from utils.test import ServiceTestMixin


container = get_di_test_container()


class TestCheckPassword(ServiceTestMixin):
    def test_check_match(self, mocker: MockerFixture):
        bcrypt = mocker.patch("services.password.check.bcrypt")
        bcrypt.checkpw.return_value = True

        result = container.check_password()("plain", "hashed")

        assert result
        bcrypt.checkpw.assert_called_once_with(
            "plain".encode("utf-8"), "hashed".encode("utf-8")
        )

    def test_check_mismatch(self, mocker: MockerFixture):
        bcrypt = mocker.patch("services.password.check.bcrypt")
        bcrypt.checkpw.return_value = False

        result = container.check_password()("plain", "hashed")

        assert not result
        bcrypt.checkpw.assert_called_once_with(
            "plain".encode("utf-8"), "hashed".encode("utf-8")
        )
