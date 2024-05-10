import logging
import asyncio
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from typing import Callable

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)
from sqlalchemy.orm import (
    declarative_base,
)
from sqlalchemy.exc import SQLAlchemyError


logger = logging.getLogger("orm")
Base = declarative_base()


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, future=True, echo=True)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                class_=AsyncSession,
                autocommit=False,
                autoflush=True,
                bind=self._engine,
            ),
            scopefunc=asyncio.current_task,
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession = self._session_factory()
        try:
            print("YIELDING...")
            yield session
        except Exception as e:
            print("ROLLBACKING... ")
            await session.rollback()
            print("ERROR... ", str(e))
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            raise
        else:
            print("COMMITTING... ")
            try:
                await session.commit()
            except SQLAlchemyError as e:
                print("ERROR COMMITTING...", str(e))
                await session.rollback()
                logger.error(
                    f"Session rollback because of exception on commit - {str(e)}",
                    exc_info=e,
                )
        finally:
            print("CLOSING... ")
            await session.close()
