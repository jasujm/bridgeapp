"""
Tests for the :mod:`bridgeapp.api` module
"""

import unittest.mock
import uuid

import fastapi
import fastapi.testclient
import pytest

from bridgeapp import models, app


@pytest.fixture
def client():
    return fastapi.testclient.TestClient(app)


@pytest.fixture
def mock_bridge_client(monkeypatch):
    from bridgeapp.web import api
    mock = unittest.mock.Mock(
        game=unittest.mock.AsyncMock(), join=unittest.mock.AsyncMock()
    )
    monkeypatch.setattr(api._bridgeprotocol, "get_client", lambda: mock)
    return mock


def test_create_game(client, mock_bridge_client):
    game_uuid = uuid.uuid4()
    mock_bridge_client.game.return_value = game_uuid
    res = client.post("/api/v1/games")
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    assert res.headers["Location"] == f"/api/v1/games/{game_uuid}"
    assert res.json() == {"uuid": str(game_uuid)}


def test_add_player(client, mock_bridge_client):
    game_uuid = uuid.uuid4()
    player_uuid = uuid.uuid4()
    res = client.post(
        f"/api/v1/games/{game_uuid}/players", json={"uuid": str(player_uuid)}
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    assert mock_bridge_client.called_once_with(game=game_uuid, player=player_uuid)
