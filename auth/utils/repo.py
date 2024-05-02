from abc import ABC
from typing import Callable
from dataclasses import fields

from fastapi import Depends
from sqlalchemy.orm import Session


class IRepo(ABC):
    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self.session_factory = session_factory
        self.session = Depends(session_factory)


def pagination_transformer(schema: Callable) -> Callable:
    return lambda query: tuple(
        schema(**{field.name: getattr(item, field.name) for field in fields(schema)})
        for item in query
    )
