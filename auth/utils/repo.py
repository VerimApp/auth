from abc import ABC
from contextlib import AbstractAsyncContextManager
from typing import Callable
from dataclasses import fields

from sqlalchemy.ext.asyncio import AsyncSession


class IRepo(ABC):
    pass


def pagination_transformer(schema: Callable) -> Callable:
    return lambda query: tuple(
        schema(**{field.name: getattr(item, field.name) for field in fields(schema)})
        for item in query
    )
