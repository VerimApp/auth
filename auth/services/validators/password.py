from typing import List
import string

from .base import LengthValidator, CharactersValidator, IValidator
from ..entries import PasswordRequiredCharactersGroup
from config.i18n import _
from utils.exceptions import Custom400Exception


class PasswordLengthValidator(LengthValidator):
    error_messages = {
        "min_length": lambda min_length: _(
            "Make sure that password length is not less than %(min_length)s."
        )
        % {"min_length": min_length},
        "max_length": lambda max_length: _(
            "Make sure that password length is not greater than %(max_length)s."
        )
        % {"max_length": max_length},
    }


class PasswordCharactersValidator(CharactersValidator):
    error_messages = {
        "invalid_characters": lambda invalid_characters: _(
            "Invalid characters in password: %(invalid_characters)s."
        )
        % {"invalid_characters": ", ".join(invalid_characters)}
    }


class PasswordRequiredCharactersValidator(IValidator):
    def __init__(self, *characters_groups: PasswordRequiredCharactersGroup) -> None:
        self.groups = characters_groups

    def is_valid(self, data: str, raise_exception: bool) -> bool:
        present_in_password = {group.name: False for group in self.groups}
        for letter in data:
            for group in self.groups:
                if present_in_password.get(group.name):
                    continue
                if letter in group.characters:
                    present_in_password[group.name] = True
                    continue

        not_present_in_password = [
            group
            for group, is_present in present_in_password.items()
            if is_present is False
        ]
        if raise_exception and not_present_in_password:
            raise Custom400Exception(
                _(
                    "Password must contain at least one character from each of the"
                    " following groups:\n"
                )
                + "\n".join([group.description for group in self.groups])
            )

        return False if not_present_in_password else True


def get_password_required_groups() -> List[PasswordRequiredCharactersGroup]:
    return [
        PasswordRequiredCharactersGroup(
            name="lowercase",
            characters=string.ascii_lowercase,
            description=_("- Lowercase letters"),
        ),
        PasswordRequiredCharactersGroup(
            name="uppercase",
            characters=string.ascii_uppercase,
            description=_("- Uppercase letters"),
        ),
        PasswordRequiredCharactersGroup(
            name="digits", characters=string.digits, description=_("- Digits")
        ),
    ]
