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


logger = logging.getLogger("orm")
Base = declarative_base()


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(db_url, future=True, echo=True)
        self._session_factory = async_scoped_session(
            async_sessionmaker(
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
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
            yield session
        except Exception as e:
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            await session.rollback()
            raise
        finally:
            session.expunge_all()
            await session.close()
