"""
Tests for the :mod:`bridgeapp.api` module
"""

import unittest.mock
import uuid

import fastapi
import fastapi.testclient
import pytest

from bridgeapp import app, api, models


@pytest.fixture
def client():
    """Yield mock client that interacts with the API"""
    return fastapi.testclient.TestClient(app)


@pytest.fixture
def mock_bridge_client(monkeypatch):
    """Yield mock client that will be used by the API to interact with the bridge backend"""
    mock = unittest.mock.Mock(
        game=unittest.mock.AsyncMock(),
        join=unittest.mock.AsyncMock(),
        get_deal=unittest.mock.AsyncMock(),
    )
    monkeypatch.setattr(api.utils, "get_bridge_client", lambda: mock)
    return mock


@pytest.fixture
def game_uuid():
    """Yield an UUID for game"""
    return uuid.uuid4()


@pytest.fixture(params=["username", "anotheruser"])
def username(request):
    """Yield an username"""
    return request.param


@pytest.fixture
def username_and_player_uuid(username):
    """Yield a pair containing an username and corresponding player UUID"""
    return username, api.utils.generate_player_uuid(username)


def test_generate_player_uuid():
    assert isinstance(api.utils.generate_player_uuid("username"), uuid.UUID)


def test_create_game(client, mock_bridge_client, game_uuid, username):
    mock_bridge_client.game.return_value = game_uuid
    res = client.post("/api/v1/games", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    assert res.headers["Location"] == f"/api/v1/games/{game_uuid}"
    assert res.json() == {"uuid": str(game_uuid)}


def test_read_game(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    deal_state = models.DealState(positionInTurn=models.Position.north)
    mock_bridge_client.get_deal.return_value = deal_state
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert api.models.Game(**res.json()) == {"uuid": game_uuid, "deal": deal_state}
    mock_bridge_client.get_deal.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_add_player(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    mock_bridge_client.join.return_value = None
    res = client.post(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(game=game_uuid, player=player_uuid)
