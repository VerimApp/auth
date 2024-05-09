import logging
from contextlib import contextmanager, AbstractContextManager
from typing import Callable

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    Session,
    declarative_base,
    scoped_session,
)


logger = logging.getLogger("orm")
Base = declarative_base()


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def create_database(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception as e:
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            session.rollback()
            raise
        finally:
            session.expunge_all()
            session.close()
