"""
Global test config
"""

import asyncio
import uuid
import random

import databases
import pytest
import sqlalchemy

from bridgeapp import db

# TODO: It would be very much preferable to have asynchronous database fixture
# and run it in asynchronous test cases... but the test client shipped with
# FastAPI doesn't as of yet support asynchronous use and assumes it is not run
# in event loop. So until that's changed, unit tests need to run asynchronous DB
# calls synchronously.


@pytest.fixture
def database(monkeypatch, tmpdir):
    """Yield database connection with empty tables created"""
    dbfile = f"sqlite:///{tmpdir}/test.db"
    engine = sqlalchemy.create_engine(dbfile)
    db.meta.create_all(engine)
    try:
        database = databases.Database(dbfile)
        asyncio.run(database.connect())
        monkeypatch.setattr(db, "get_database", lambda: database)
        yield database
    finally:
        asyncio.run(database.disconnect())


@pytest.fixture
def game_id():
    """Yield an UUID for game"""
    return uuid.uuid4()


@pytest.fixture
def player_id():
    """Yield an UUID for player"""
    return uuid.uuid4()


@pytest.fixture
def username():
    """Yield a username for player"""
    return "".join(random.sample("abcdefghijklmnopqrstuvwxyz", 15))
