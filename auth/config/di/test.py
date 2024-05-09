from dependency_injector import containers, providers

from config import settings
from config.db import Database
from config.di.dev import Container


@containers.copy(Container)
class TestContainer(containers.DeclarativeContainer):
    db = providers.Singleton(
        Database, db_url=settings.TEST_DATABASE_URL
    )
