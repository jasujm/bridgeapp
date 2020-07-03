"""
Tests for the :mod:`bridgeapp.api` module
"""

import unittest.mock
import uuid

import fastapi
import fastapi.testclient
import pytest

from bridgeapp import app, api, bridgeprotocol, models


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
        get_self=unittest.mock.AsyncMock(),
        call=unittest.mock.AsyncMock(),
        play=unittest.mock.AsyncMock(),
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
    assert res.headers["Location"] == f"http://testserver/api/v1/games/{game_uuid}"
    assert api.models.Game(**res.json()) == api.models.Game(uuid=game_uuid)


def test_create_game_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.game.side_effect = bridgeprotocol.CommandFailure
    res = client.post("/api/v1/games", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_400_BAD_REQUEST
    mock_bridge_client.game.assert_awaited_once()


def test_read_game(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    deal = models.Deal(uuid=uuid.uuid4())
    mock_bridge_client.get_deal.return_value = deal
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert api.models.Game(**res.json()) == {"uuid": game_uuid, "deal": deal}
    mock_bridge_client.get_deal.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_read_game_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_deal.side_effect = bridgeprotocol.CommandFailure
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_400_BAD_REQUEST
    mock_bridge_client.get_deal.assert_awaited_once()


def test_read_self(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    player_state = models.PlayerState(position=models.Position.north)
    mock_bridge_client.get_self.return_value = player_state
    res = client.get(f"/api/v1/games/{game_uuid}/self", auth=(username, "secret"))
    assert models.PlayerState(**res.json()) == player_state
    mock_bridge_client.get_self.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_read_game_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_self.side_effect = bridgeprotocol.CommandFailure
    res = client.get(f"/api/v1/games/{game_uuid}/self", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_400_BAD_REQUEST
    mock_bridge_client.get_self.assert_awaited_once()


def test_add_player(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    mock_bridge_client.join.return_value = None
    res = client.post(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(game=game_uuid, player=player_uuid)


def test_add_player_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.join.side_effect = bridgeprotocol.CommandFailure
    res = client.post(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_400_BAD_REQUEST
    mock_bridge_client.join.assert_awaited_once()


def test_make_call(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    call = models.Call(
        type=models.CallType.bid, bid=models.Bid(level=4, strain=models.Strain.spades)
    )
    mock_bridge_client.call.return_value = None
    res = client.post(
        f"/api/v1/games/{game_uuid}/calls", auth=(username, "secret"), data=call.json()
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.call.assert_awaited_once_with(
        game=game_uuid, player=player_uuid, call=call
    )


def test_make_call_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    call = models.Call(type=models.CallType.pass_)
    mock_bridge_client.call.side_effect = bridgeprotocol.CommandFailure
    res = client.post(
        f"/api/v1/games/{game_uuid}/calls", auth=(username, "secret"), data=call.json()
    )
    assert res.status_code == fastapi.status.HTTP_400_BAD_REQUEST
    mock_bridge_client.call.assert_awaited_once()


def test_play_card(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    card = models.CardType(rank=models.Rank.queen, suit=models.Suit.hearts)
    mock_bridge_client.play.return_value = None
    res = client.post(
        f"/api/v1/games/{game_uuid}/trick", auth=(username, "secret"), data=card.json()
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.play.assert_awaited_once_with(
        game=game_uuid, player=player_uuid, card=card
    )


def test_play_card_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    card = models.CardType(rank=models.Rank.seven, suit=models.Suit.diamonds)
    mock_bridge_client.play.side_effect = bridgeprotocol.CommandFailure
    res = client.post(
        f"/api/v1/games/{game_uuid}/trick", auth=(username, "secret"), data=card.json()
    )
    assert res.status_code == fastapi.status.HTTP_400_BAD_REQUEST
    mock_bridge_client.play.assert_awaited_once()
