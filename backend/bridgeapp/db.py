"""
Database definitions
....................
"""

import asyncio
import logging
import typing

import sqlalchemy
import sqlalchemy.ext.asyncio as sqlaio
import sqlalchemy_utils.types as sqlt

from .settings import settings

# monkey patch pydantic to be compatible with asyncpg
try:
    from pydantic.json import ENCODERS_BY_TYPE
    import asyncpg.pgproto.pgproto
except ImportError:
    pass
else:
    ENCODERS_BY_TYPE[asyncpg.pgproto.pgproto.UUID] = str


logger = logging.getLogger(__name__)


def _get_timestamp_columns():
    return [
        sqlalchemy.Column(
            "createdAt",
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=sqlalchemy.func.now(),  # pylint: disable=not-callable
        ),
        sqlalchemy.Column(
            "updatedAt",
            sqlalchemy.DateTime(timezone=True),
            nullable=False,
            default=sqlalchemy.func.now(),  # pylint: disable=not-callable
            onupdate=sqlalchemy.func.now(),  # pylint: disable=not-callable
        ),
    ]


engine = sqlaio.create_async_engine(settings.database_url)

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
    sqlalchemy.Column("name", sqlalchemy.String(63), nullable=False),
    sqlalchemy.Column("isPublic", sqlalchemy.Boolean, nullable=False),
    *_get_timestamp_columns(),
)


def get_engine() -> sqlaio.AsyncEngine:
    """Get database engine"""
    return engine


def get_connection() -> typing.AsyncContextManager[sqlaio.AsyncConnection]:
    """Get database connection"""
    return get_engine().begin()


async def _init(_engine):
    async with _engine.begin() as conn:
        await conn.run_sync(meta.create_all)


def init():
    """Initializes databases"""
    asyncio.run(_init(engine))
    logger.info("Database tables created")
