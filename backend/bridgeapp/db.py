"""
Database definitions
....................
"""

import logging

import databases
import sqlalchemy
import sqlalchemy_utils.types as sqlt

from .settings import settings

logger = logging.getLogger(__name__)


def _get_database_url():
    # TODO: Using aiopg since the default (asyncpg) doesn't work with
    # sqlalchemy_utils UUID type. Needs to be investigated.
    url = databases.DatabaseURL(settings.database_url)
    if url.dialect == "postgresql":
        url = url.replace(dialect="postgresql+aiopg")
    return url


def _get_timestamp_columns():
    return [
        sqlalchemy.Column(
            "createdAt",
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=sqlalchemy.func.now(),
        ),
        sqlalchemy.Column(
            "updatedAt",
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=sqlalchemy.func.now(),
            onupdate=sqlalchemy.func.now(),
        ),
    ]


database = databases.Database(_get_database_url())

meta = sqlalchemy.MetaData()

players = sqlalchemy.Table(
    "players",
    meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column(
        "username", sqlalchemy.String(31), nullable=False, index=True, unique=True
    ),
    sqlalchemy.Column(
        "password",
        sqlt.password.PasswordType(schemes=["pbkdf2_sha512"]),
        nullable=False,
    ),
    *_get_timestamp_columns(),
)

games = sqlalchemy.Table(
    "games",
    meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(63), nullable=False, index=True),
    sqlalchemy.Column("isPublic", sqlalchemy.Boolean, nullable=False),
    *_get_timestamp_columns(),
)


def get_database():
    """Get database connection"""
    return database


def init():
    """Initializes databases"""
    engine = sqlalchemy.create_engine(settings.database_url)
    meta.create_all(engine)
    logger.info("Database tables created")
