from pytest_mock import MockerFixture

from config.di import get_di_test_container
from utils.test import ServiceTestMixin


container = get_di_test_container()


class TestHashassword(ServiceTestMixin):
    def test_check_match(self, mocker: MockerFixture):
        bcrypt = mocker.patch("services.password.hash.bcrypt")
        bcrypt.hashpw.return_value = "hashed".encode("utf-8")
        bcrypt.gensalt.return_value = "salt".encode("utf-8")

        password = container.hash_password()("password")

        assert password == "hashed"
        bcrypt.hashpw.assert_called_once_with(
            "password".encode("utf-8"), "salt".encode("utf-8")
        )
        bcrypt.gensalt.assert_called_once_with()
