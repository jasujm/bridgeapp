"""
Database utilities
..................
"""

import contextlib
import uuid
import typing

import sqlalchemy
import sqlalchemy.exc as sqlexc
import sqlalchemy.ext.asyncio as sqlaio

from .. import db


class NotFoundError(Exception):
    """Loaded object not found in the database"""


class AlreadyExistsError(Exception):
    """Trying to create object that already exists"""


def _begin_connection(
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
) -> typing.AsyncContextManager[sqlaio.AsyncConnection]:
    if connection:
        return contextlib.nullcontext(connection)
    return db.get_connection()


async def load(
    table: sqlalchemy.Table,
    obj_id: uuid.UUID,
    *,
    key=None,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Load attributes of an object from database

    This is a thin wrapper over selecting a row from a database table by ID.

    Parameters:
        table: The database table
        obj_id: The id to access
        key: The column used as key (defaults to ``id``)

    Returns:
        Attributes of the object

    Raises:
        :exc:`NotFoundError`: If the object is not found in the database
    """
    key_col = key if key is not None else table.c.id
    async with _begin_connection(connection) as conn:
        try:
            result = await conn.execute(
                sqlalchemy.select([table]).where(key_col == obj_id)
            )
            return result.one()
        except sqlexc.NoResultFound as ex:
            raise NotFoundError(f"{obj_id} not found") from ex


async def select(
    expression: sqlalchemy.sql.Select,
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Execute general SELECT expression

    This is a very thin wrapper over selecting rows from a
    database. It does little more than provide the database handle for
    you, and return the fetched rows.

    For retrieving a single row by primary/unique key, consider using
    :func:`load()` instead.

    Parameters:
        expression: The SELECT expression

    Returns:
        The selected rows
    """
    async with _begin_connection(connection) as conn:
        return await conn.execute(expression)


async def create(
    table: sqlalchemy.Table,
    obj_id: uuid.UUID,
    attrs: typing.Mapping[str, typing.Any],
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Create object with given attributes in database

    This is a thin wrapper over inserting a row into a table

    Parameters:
        table: The database table
        obj_id: The id of the object to create
        attrs: The attributes to insert
    """
    async with _begin_connection(connection) as conn:
        try:
            await conn.execute(table.insert(), {"id": obj_id, **attrs})
        except sqlexc.IntegrityError as ex:
            raise AlreadyExistsError(f"{obj_id} already exists") from ex


async def update(
    table: sqlalchemy.Table,
    obj_id: uuid.UUID,
    attrs: typing.Mapping[str, typing.Any],
    *,
    connection: typing.Optional[sqlaio.AsyncConnection] = None,
):
    """Update object in a database

    This is a thin wrapper over updating a row in a table

    Parameters:
        table: The database table
        obj_id: The id of the object to modify
        attrs: The new attributes
    """
    async with _begin_connection(connection) as conn:
        await conn.execute(
            sqlalchemy.update(table).where(table.c.id == obj_id).values(**attrs)
        )
