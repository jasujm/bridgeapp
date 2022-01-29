"""
API test config
"""

import asyncio
import dataclasses
import unittest.mock

import fastapi.testclient
import pytest

from bridgeapp import application, db
from bridgeapp.api import db_utils, search_utils


@dataclasses.dataclass
class MockSeach:
    index: unittest.mock.AsyncMock
    update: unittest.mock.AsyncMock
    remove: unittest.mock.AsyncMock
    search: unittest.mock.AsyncMock


@pytest.fixture
def client():
    """Yield mock client that interacts with the API"""
    return fastapi.testclient.TestClient(application)


@pytest.fixture
def password(username):
    """Yield a password for player"""
    return username[::-1]


@pytest.fixture
def db_player(player_id, username, password, database):
    asyncio.run(
        db_utils.create(
            db.players, player_id, {"username": username, "password": password}
        )
    )


@pytest.fixture
def credentials(username, password, db_player):
    """Yield credentials for API call"""
    return username, password


@pytest.fixture(params=["my game", "other game"])
def db_game(request, game_id, database):
    name = request.param
    asyncio.run(db_utils.create(db.games, game_id, {"name": name, "isPublic": True}))
    return name


@pytest.fixture
def mock_search(monkeypatch):
    ret = MockSeach(
        index=unittest.mock.AsyncMock(),
        update=unittest.mock.AsyncMock(),
        remove=unittest.mock.AsyncMock(),
        search=unittest.mock.AsyncMock(),
    )
    monkeypatch.setattr(search_utils, "index", ret.index)
    monkeypatch.setattr(search_utils, "update", ret.update)
    monkeypatch.setattr(search_utils, "remove", ret.remove)
    monkeypatch.setattr(search_utils, "search", ret.search)
    return ret
