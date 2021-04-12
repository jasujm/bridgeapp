"""
API test config
"""

import asyncio
import fastapi
import pytest

from bridgeapp import application, db
from bridgeapp.api import db_utils


@pytest.fixture
def client():
    """Yield mock client that interacts with the API"""
    return fastapi.testclient.TestClient(application)


@pytest.fixture
def password(username):
    """Yield a password for player"""
    return username[::-1]


@pytest.fixture
def credentials(player_id, username, password, database):
    """Yield credentials for API call"""
    asyncio.run(
        db_utils.create(
            db.players,
            player_id,
            {"username": username, "password": password},
            database=database,
        )
    )
    return username, password
