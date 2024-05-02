from dependency_injector import containers, providers

from config import settings
from config.db import SessionFactory
from config.di.dev import Container


@containers.copy(Container)
class TestContainer(containers.DeclarativeContainer):
    db_session_factory = providers.Singleton(
        SessionFactory, db_url=settings.TEST_DATABASE_URL
    )
