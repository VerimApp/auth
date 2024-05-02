import logging
from typing import Iterable

from sqlalchemy.exc import SQLAlchemyError

from utils.exceptions import CustomException, Custom400Exception


orm_logger = logging.getLogger("orm")
grpc_logger = logging.getLogger("grpc")


def handle_grpc_request_error(return_class):
    def outer(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
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


def apply_tags(tags: Iterable[str]):
    """
    Декоратор используется для добавления тегов к роутерам
    """

    def outer(func):
        def inner(*args, **kwargs):
            routers = func(*args, **kwargs)
            for router in routers:
                router.tags = list(set([*(router.tags or list()), *tags]))
            return routers

        return inner

    return outer


def handle_orm_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            orm_logger.error(
                f"Error while processing orm query - {str(e)}",
                extra={"func_args": args, "func_kwargs": kwargs},
                exc_info=e,
            )
            raise

    return wrapper
