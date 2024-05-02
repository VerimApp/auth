import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    sessionmaker,
    Session,
    declarative_base,
    scoped_session,
)


logger = logging.getLogger("orm")
Base = declarative_base()


class SessionFactory:
    def __init__(self, db_url: str) -> None:
        self._engine = create_engine(db_url, echo=True)
        self._session_factory = scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def __call__(self) -> Session:
        session = self._session_factory()
        try:
            print("YIELD")
            yield session
        except Exception as e:
            print("ERROR")
            logger.error(
                f"Session rollback because of exception - {str(e)}", exc_info=e
            )
            session.rollback()
            raise
        else:
            print("COMMIT")
            session.commit()
        finally:
            print("CLOSE")
            session.expunge_all()
            session.close()
