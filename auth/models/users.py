from sqlalchemy import Table, Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import registry


mapper_registry = registry()


user_table = Table(
    "auth_user",
    mapper_registry.metadata,
    Column(
        "id", Integer, primary_key=True, unique=True, autoincrement=True, nullable=False
    ),
    Column("email", String(50), unique=True, nullable=False),
    Column("username", String(35), unique=True, nullable=False),
    Column("password", String(128), nullable=True),
    Column("first_name", String(50), nullable=True),
    Column("last_name", String(50), nullable=True),
    Column("is_active", Boolean, default=True, nullable=False),
    Column(
        "created_at", DateTime(timezone=True), server_default=func.now(), nullable=False
    ),
    Column(
        "updated_at",
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    ),
    Column("tokens_revoked_at", DateTime(timezone=True), default=None, nullable=True),
    Column(
        "email_confirmed",
        Boolean,
        default=False,
        server_default="false",
        nullable=False,
    ),
)


class User:
    pass


user_mapper = mapper_registry.map_imperatively(User, user_table)
