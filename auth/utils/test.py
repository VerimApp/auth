from typing import Dict
from types import SimpleNamespace

import pytest


class SchemaTestMixin:
    schema_class = None

    def assertValid(self, data: Dict) -> None:
        self.schema_class(**data)

    def assertNotValid(self, data: Dict) -> None:
        with pytest.raises(ValueError):
            self.schema_class(**data)


class ServiceTestMixin:
    service = None
    user = SimpleNamespace(
        **{
            "id": 1,
            "username": "testuser",
            "email": "testuser@email.com",
            "password": "testpassword",
            "email_confirmed": True,
            "is_active": True,
            "tokens_revoked_at": None,
        }
    )


class RepoTestMixin:
    repo = None
