from abc import ABC, abstractmethod
from typing import Any
from enum import Enum

from config.i18n import _
from utils.exceptions import Custom400Exception


class ValidationMode(Enum):
    OR = "OR"
    AND = "AND"


class IValidate(ABC):
    @abstractmethod
    def __call__(
        self,
        data: Any,
        *,
        mode: ValidationMode = ValidationMode.AND,
        raise_exception: bool = True
    ) -> bool: ...


class IValidator(ABC):
    @abstractmethod
    def is_valid(self, data: Any, raise_exception: bool) -> bool: ...


class Validate(IValidate):
    def __init__(self, *validators: IValidator):
        self.validators = validators

    def __call__(
        self,
        data: Any,
        *,
        mode: ValidationMode = ValidationMode.AND,
        raise_exception: bool = True
    ) -> None:
        is_valid = True
        for validator in self.validators:
            is_valid = validator.is_valid(data, raise_exception)
            if mode == ValidationMode.AND and not is_valid:
                return is_valid
            if mode == ValidationMode.OR and is_valid:
                return is_valid
        return is_valid


class LengthValidator(IValidator):
    error_messages = {
        "min_length": lambda min_length: _(
            "Make sure that length is not less than %(min_length)s."
        )
        % {"min_length": min_length},
        "max_length": lambda max_length: _(
            "Make sure that length is not greater than %(max_length)s."
        )
        % {"max_length": max_length},
    }

    def __init__(self, min_length: int, max_length: int) -> None:
        self.min_length = min_length
        self.max_length = max_length

    def is_valid(self, data: Any, raise_exception: bool = True) -> bool:
        is_valid = True
        if len(data) < self.min_length:
            if raise_exception:
                raise Custom400Exception(
                    self.error_messages["min_length"](self.min_length)
                )
            is_valid = False
        if len(data) > self.max_length:
            if raise_exception:
                raise Custom400Exception(
                    self.error_messages["max_length"](self.max_length)
                )
            is_valid = False
        return is_valid


class CharactersValidator(IValidator):
    error_messages = {
        "invalid_characters": lambda invalid_characters: _(
            "Invalid characters: %(invalid_characters)s."
        )
        % {"invalid_characters": ", ".join(invalid_characters)}
    }

    def __init__(self, valid_characters: str) -> None:
        self.valid_characters = valid_characters

    def is_valid(self, data: str, raise_exception: bool = True) -> bool:
        is_valid = True
        invalid_characters = []
        for letter in data:
            if letter not in self.valid_characters:
                invalid_characters.append(letter)
                is_valid = False

        if invalid_characters and raise_exception:
            raise Custom400Exception(
                self.error_messages["invalid_characters"](invalid_characters)
            )
        return is_valid
