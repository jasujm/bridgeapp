"""
Database definitions
....................
"""

import databases
import sqlalchemy
import sqlalchemy_utils.types as sqlt

from .settings import settings

# from .bridgeprotocol import models


def _get_database_url():
    # TODO: Using aiopg since the default (asyncpg) doesn't work with
    # sqlalchemy_utils UUID type. Needs to be investigated.
    url = databases.DatabaseURL(settings.database_url)
    if url.dialect == "postgresql":
        url = url.replace(dialect="postgresql+aiopg")
    return url


database = databases.Database(_get_database_url())

engine = sqlalchemy.create_engine(settings.database_url)
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
)

games = sqlalchemy.Table(
    "games",
    meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(63), nullable=False, index=True),
)

"""
Not sure if needed

game_players = sqlalchemy.Table(
    "game_players",
    meta,
    sqlalchemy.Column(
        "game_id",
        sqlt.uuid.UUIDType,
        sqlalchemy.ForeignKey(games.c.id),
        primary_key=True,
    ),
    sqlalchemy.Column("position", sqlalchemy.Enum(models.Position), primary_key=True),
    sqlalchemy.Column(
        "player_id",
        sqlt.uuid.UUIDType,
        sqlalchemy.ForeignKey(players.c.id),
        nullable=False,
    ),
)
"""

meta.create_all(engine)


def get_database():
    """Get database connection"""
    return database
