from unittest import mock

import pytest

from services.validators import Validate, LengthValidator, CharactersValidator
from services.validators.base import ValidationMode
from utils.test import ServiceTestMixin
from utils.exceptions import Custom400Exception


class TestValidate(ServiceTestMixin):
    def setup_method(self):
        self.data = None

        self.validator1 = mock.Mock()
        self.validator1.is_valid.return_value = True

        self.validator2 = mock.Mock()
        self.validator2.is_valid.return_value = True

        self.validate = Validate(self.validator1, self.validator2)

    def test_and_mode_both_valid(self):
        assert self.validate(self.data, mode=ValidationMode.AND, raise_exception=False)
        self.validator1.is_valid.assert_called_once_with(self.data, False)
        self.validator2.is_valid.assert_called_once_with(self.data, False)

    def test_and_mode_first_valid(self):
        self.validator2.is_valid.return_value = False
        assert not self.validate(
            self.data, mode=ValidationMode.AND, raise_exception=False
        )
        self.validator1.is_valid.assert_called_once_with(self.data, False)
        self.validator2.is_valid.assert_called_once_with(self.data, False)

    def test_and_mode_second_valid(self):
        self.validator1.is_valid.return_value = False
        assert not self.validate(
            self.data, mode=ValidationMode.AND, raise_exception=False
        )
        self.validator1.is_valid.assert_called_once_with(self.data, False)
        self.validator2.is_valid.assert_not_called()

    def test_and_mode_both_not_valid(self):
        self.validator1.is_valid.return_value = False
        self.validator2.is_valid.return_value = False
        assert not self.validate(
            self.data, mode=ValidationMode.AND, raise_exception=False
        )
        self.validator1.is_valid.assert_called_once_with(self.data, False)
        self.validator2.is_valid.assert_not_called()

    def test_or_mode_both_valid(self):
        assert self.validate(self.data, mode=ValidationMode.OR, raise_exception=True)
        self.validator1.is_valid.assert_called_once_with(self.data, True)
        self.validator2.is_valid.assert_not_called()

    def test_or_mode_first_valid(self):
        self.validator2.is_valid.return_value = False
        assert self.validate(self.data, mode=ValidationMode.OR, raise_exception=True)
        self.validator1.is_valid.assert_called_once_with(self.data, True)
        self.validator2.is_valid.assert_not_called()

    def test_or_mode_second_valid(self):
        self.validator1.is_valid.return_value = False
        assert self.validate(self.data, mode=ValidationMode.OR, raise_exception=True)
        self.validator1.is_valid.assert_called_once_with(self.data, True)
        self.validator2.is_valid.assert_called_once_with(self.data, True)

    def test_or_mode_both_not_valid(self):
        self.validator1.is_valid.return_value = False
        self.validator2.is_valid.return_value = False
        assert not self.validate(
            self.data, mode=ValidationMode.OR, raise_exception=True
        )
        self.validator1.is_valid.assert_called_once_with(self.data, True)
        self.validator2.is_valid.assert_called_once_with(self.data, True)


class TestLengthValidator(ServiceTestMixin):
    def setup_method(self):
        self.min_length = 1
        self.max_length = 10

        self.validator = LengthValidator(self.min_length, self.max_length)

    def test_less_than_min(self):
        assert not self.validator.is_valid(
            "a" * (self.min_length - 1), raise_exception=False
        )

    def test_less_than_min_raise_exc(self):
        with pytest.raises(Custom400Exception):
            self.validator.is_valid("a" * (self.min_length - 1), raise_exception=True)

    def test_more_than_max(self):
        assert not self.validator.is_valid(
            "a" * (self.max_length + 1), raise_exception=False
        )

    def test_more_than_max_raise_exc(self):
        with pytest.raises(Custom400Exception):
            self.validator.is_valid("a" * (self.max_length + 1), raise_exception=True)

    def test_validator(self):
        assert self.validator.is_valid("a" * (self.max_length - 1))


class TestCharacterValidator(ServiceTestMixin):
    def setup_method(self):
        self.valid_characters = "abcde"

        self.validator = CharactersValidator(self.valid_characters)

    def test_invalid_characters(self):
        assert not self.validator.is_valid("abcdf", raise_exception=False)

    def test_invalid_characters_raise_exc(self):
        with pytest.raises(Custom400Exception):
            self.validator.is_valid("abcdf", raise_exception=True)

    def test_validator(self):
        assert self.validator.is_valid("abcdeabcde")
