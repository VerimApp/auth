from abc import ABC
from contextlib import AbstractContextManager
from typing import Callable
from dataclasses import fields

from sqlalchemy.orm import Session


class IRepo(ABC):
    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]) -> None:
        self.session_factory = session_factory


def pagination_transformer(schema: Callable) -> Callable:
    return lambda query: tuple(
        schema(**{field.name: getattr(item, field.name) for field in fields(schema)})
        for item in query
    )
