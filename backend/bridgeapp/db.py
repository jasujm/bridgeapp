"""
Database definitions
....................
"""

import databases
import sqlalchemy
import sqlalchemy_utils.types as sqlt

from .settings import settings

database = databases.Database(settings.database_url)

engine = sqlalchemy.create_engine(settings.database_url)
meta = sqlalchemy.MetaData()

players = sqlalchemy.Table(
    "players",
    meta,
    sqlalchemy.Column("id", sqlt.uuid.UUIDType, primary_key=True),
    sqlalchemy.Column("username", sqlalchemy.String(15)),
)

meta.create_all(engine)


def get_database():
    """Get database connection"""
    return database
