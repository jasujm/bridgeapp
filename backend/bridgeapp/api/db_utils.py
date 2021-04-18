"""
Database utilities
..................
"""

import uuid
import sqlite3
import typing

import psycopg2
import sqlalchemy
import sqlalchemy.exc as sqlexc

from .. import db


class NotFoundError(Exception):
    """Loaded object not found in the database"""


class AlreadyExistsError(Exception):
    """Trying to create object that already exists"""


def _get_database(database):
    return database if database else db.get_database()


async def load(table: sqlalchemy.Table, obj_id: uuid.UUID, *, key=None, database=None):
    """Load attributes of an object from database

    This is a thin wrapper over selecting a row from a database table by ID.

    Parameters:
        table: The database table
        id: The id to access
        key: The column used as key (defaults to ``id``)
        database: The database connection to use, or ``None`` to use the
                  default database

    Returns:
        Attributes of the object

    Raises:
        :exc:`NotFoundError`: If the object is not found in the database
    """
    database = _get_database(database)
    key_col = key if key is not None else table.c.id
    if obj := await database.fetch_one(
        query=sqlalchemy.select([table]).where(key_col == obj_id)
    ):
        return obj
    raise NotFoundError(f"{obj_id} not found")


async def select(expression: sqlalchemy.sql.Select, *, database=None):
    """Execute general SELECT expression

    This is a very thin wrapper over selecting rows from a
    database. It does little more than provide the database handle for
    you, and return the fetched rows.

    For retrieving a single row by primary/unique key, consider using
    :func:`load()` instead.

    Parameters:
        expression: The SELECT expression
        database: The database connection to use, or ``None`` to use the
                  default database

    Returns:
        The selected rows
    """
    database = _get_database(database)
    return await database.fetch_all(expression)


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
    try:
        await database.execute(query=table.insert(), values={"id": obj_id, **attrs})
    except (
        sqlexc.IntegrityError,
        sqlite3.IntegrityError,
        psycopg2.IntegrityError,
    ) as ex:
        # ^ TODO: Does the databases library use common wrapper for different
        # drivers?
        raise AlreadyExistsError(f"{obj_id} already exists") from ex


async def update(
    table: sqlalchemy.Table,
    obj_id: uuid.UUID,
    attrs: typing.Mapping[str, typing.Any],
    *,
    database=None,
):
    """Update object in a database

    This is a thin wrapper over updating a row in a table

    Parameters:
        table: The database table
        obj_id: The id of the object to modify
        attrs: The new attributes
        database: The database connection to use, or ``None`` to use the
                  default database
    """
    database = _get_database(database)
    await database.execute(
        query=sqlalchemy.update(table).where(table.c.id == obj_id).values(**attrs)
    )
