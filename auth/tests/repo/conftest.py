import subprocess

from sqlalchemy.sql import text

from config.di import get_di_test_container
from models.users import mapper_registry as user_mapper_registry
from models.codes import mapper_registry as code_mapper_registry


container = get_di_test_container()


def pytest_configure(config):
    """
    Allows plugins and conftest files to perform initial configuration.
    This hook is called for every plugin and initial conftest
    file after command line options have been parsed.
    """
    subprocess.call(["alembic", "-n", "alembic.test", "upgrade", "head"])


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
    with container.db().session() as session:
        for table in reversed(user_mapper_registry.metadata.sorted_tables):
            session.execute(text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE;"))

        for table in reversed(code_mapper_registry.metadata.sorted_tables):
            session.execute(text(f"TRUNCATE {table.name} RESTART IDENTITY CASCADE;"))

        session.commit()
