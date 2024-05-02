import pytest

from config.di import get_di_test_container
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception


container = get_di_test_container()


class TestPasswordRequiredCharactersValidator(ServiceTestMixin):
    def test_contains_all_but_lowercase(self):
        assert not container.password_required_characters_validator().is_valid(
            "A1", raise_exception=False
        )

    def test_contains_all_but_lowercase_raise_exc(self):
        with pytest.raises(Custom400Exception):
            container.password_required_characters_validator().is_valid(
                "A1", raise_exception=True
            )

    def test_contains_all_but_uppercase(self):
        assert not container.password_required_characters_validator().is_valid(
            "a1", raise_exception=False
        )

    def test_contains_all_but_uppercase_raise_exc(self):
        with pytest.raises(Custom400Exception):
            container.password_required_characters_validator().is_valid(
                "a1", raise_exception=True
            )

    def test_contains_all_but_digits(self):
        assert not container.password_required_characters_validator().is_valid(
            "Aa", raise_exception=False
        )

    def test_contains_all_but_digits_raise_exc(self):
        with pytest.raises(Custom400Exception):
            container.password_required_characters_validator().is_valid(
                "Aa", raise_exception=True
            )

    def test_validator(self):
        assert container.password_required_characters_validator().is_valid(
            "Aa1", raise_exception=True
        )
        assert container.password_required_characters_validator().is_valid(
            "Aa1", raise_exception=False
        )
