"""
Database utilities
..................
"""

import uuid
import typing

import sqlalchemy

from .. import db


class NotFoundError(Exception):
    """Loaded object not found in the database"""


def _get_database(database):
    return database if database else db.get_database()


async def load(table: sqlalchemy.Table, obj_id: uuid.UUID, *, database=None):
    """Load attributes of an object from database

    This is a thin wrapper over selecting a row from a database table by ID.

    Parameters:
        table: The database table
        id: The id to access
        database: The database connection to use, or ``None`` to use the
                  default database

    Returns:
        Attributes of the object

    Raises:
        :exc:`NotFoundError`: If the object is not found in the database
    """
    database = _get_database(database)
    if obj := await database.fetch_all(
        query=sqlalchemy.select([table]).where(table.c.id == obj_id)
    ):
        return obj[0]
    raise NotFoundError(f"{obj_id} not found")


async def create(
    table: sqlalchemy.Table,
    obj_id: uuid.UUID,
    attrs: typing.Mapping[str, typing.Any],
    *,
    database=None,
):
    """Create object with given attributes in database

    This is a thin wrapper over inserting a row into a table

    Parameters:
        table: The database table
        obj_id: The id of the object to create
        attrs: The attributes to insert
        database: The database connection to use, or ``None`` to use the
                  default database
    """
    database = _get_database(database)
    await database.execute(query=table.insert(), values={"id": obj_id, **attrs})
