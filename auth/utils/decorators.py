import logging
from typing import ClassVar, Dict, Protocol, Any

from sqlalchemy import Row
from sqlalchemy.exc import SQLAlchemyError

from utils.exceptions import CustomException, Custom400Exception


orm_logger = logging.getLogger("orm")
grpc_logger = logging.getLogger("grpc")


def handle_grpc_request_error(return_class):
    def outer(func):
        async def inner(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except CustomException as e:
                grpc_logger.info(
                    f"Custom exception has occured - {str(e)}",
                    extra={"func_args": args, "func_kwargs": kwargs},
                    exc_info=e,
                )
                return return_class(detail=e.detail)

        return inner

    return outer


def handle_grpc_response_error(func):
    async def wrapper(*args, **kwargs):
        try:
            response = await func(*args, **kwargs)
        except Exception as e:
            grpc_logger.error(
                f"Error from gRPC response - {str(e)}",
                extra={"func_args": args, "func_kwargs": kwargs},
                exc_info=e,
            )
            raise

        if getattr(response, "detail", None):
            raise Custom400Exception(detail=response.detail)
        return response

    return wrapper


def handle_orm_error(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SQLAlchemyError as e:
            orm_logger.error(
                f"Error while processing orm query - {str(e)}",
                extra={"func_args": args, "func_kwargs": kwargs},
                exc_info=e,
            )
            raise

    return wrapper


class Dataclass(Protocol):
    __dataclass_fields__: ClassVar[Dict[str, Any]]


def row_to_model(wrapper_dataclass: Dataclass | None = None):
    """
    Конвертация объекта `Row` в модель БД или датакласс.

    В случае, когда выборка происходит по определенным столбцам таблицы/таблиц,
    объект `Row` будет содержать данные для каждого столбца, а не инстанс модели,  TODO: проверить это
    поэтому необходимо передать датакласс, который поддерживает хранение возвращаемых столбцов.
    """

    def outer(func):
        async def inner(*args, **kwargs):
            row: Row | None = await func(*args, **kwargs)
            if not row or not row._fields:
                return row

            if len(row._fields) == 1:
                return row._mapping.get(row._fields[0])

            assert (
                wrapper_dataclass is not None
            ), "Dataclass is required for row with custom column set."
            return wrapper_dataclass(**row._mapping)

        return inner

    return outer


def inject_session(func):
    async def wrapper(*args, **kwargs):
        from config.di import Container

        async with Container.db().session() as session:
            kwargs["session"] = session
            return await func(*args, **kwargs)

    return wrapper
