"""
Tests for the :mod:`bridgeapp.api` module
"""

import itertools
import unittest.mock
import uuid

import fastapi
import fastapi.testclient
import pytest

from bridgeapp import application as app, api, bridgeprotocol, models


@pytest.fixture
def client():
    """Yield mock client that interacts with the API"""
    return fastapi.testclient.TestClient(app)


@pytest.fixture
def mock_bridge_client(monkeypatch):
    """Yield mock client"""
    mock = unittest.mock.Mock(
        game=unittest.mock.AsyncMock(),
        join=unittest.mock.AsyncMock(),
        get_deal=unittest.mock.AsyncMock(),
        get_self=unittest.mock.AsyncMock(),
        call=unittest.mock.AsyncMock(),
        play=unittest.mock.AsyncMock(),
    )

    async def mock_get_bridge_client():
        return mock

    monkeypatch.setattr(
        api._bridgeprotocol, "get_bridge_client", mock_get_bridge_client
    )
    return mock


@pytest.fixture
def mock_event_receiver(monkeypatch):
    """Yield mock event receiver"""
    mock = unittest.mock.Mock(get_event=unittest.mock.AsyncMock())

    def mock_get_event_demultiplexer():
        return api._bridgeprotocol.EventDemultiplexer(mock)

    monkeypatch.setattr(
        api._bridgeprotocol, "get_event_demultiplexer", mock_get_event_demultiplexer
    )
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


def _receive_event_helper(websocket):
    return bridgeprotocol.BridgeEvent(**websocket.receive_json(mode="binary"))


def test_generate_player_uuid():
    assert isinstance(api.utils.generate_player_uuid("username"), uuid.UUID)


def test_create_game(client, mock_bridge_client, game_uuid, username):
    mock_bridge_client.game.return_value = game_uuid
    res = client.post("/api/v1/games", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    assert res.headers["Location"] == f"http://testserver/api/v1/games/{game_uuid}"
    assert api.models.Game(**res.json()) == api.models.Game(uuid=game_uuid)


def test_read_game(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    deal = models.Deal(uuid=uuid.uuid4())
    mock_bridge_client.get_deal.return_value = (deal, 123)
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert res.headers[api.games.COUNTER_HEADER] == "123"
    assert api.models.Game(**res.json()) == {"uuid": game_uuid, "deal": deal}
    mock_bridge_client.get_deal.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_read_game_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_deal.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
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


def test_read_self_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_self.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}/self", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_self.assert_awaited_once()


def test_add_player(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    mock_bridge_client.join.return_value = None
    res = client.post(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(game=game_uuid, player=player_uuid)


@pytest.mark.parametrize(
    "error",
    [
        (bridgeprotocol.NotFoundError, fastapi.status.HTTP_404_NOT_FOUND),
        (bridgeprotocol.SeatReservedError, fastapi.status.HTTP_409_CONFLICT),
    ],
)
def test_add_player_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username, error
):
    exception_class, status_code = error
    mock_bridge_client.join.side_effect = exception_class
    res = client.post(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == status_code
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


def test_make_call_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    call = models.Call(type=models.CallType.pass_)
    mock_bridge_client.call.side_effect = bridgeprotocol.NotFoundError
    res = client.post(
        f"/api/v1/games/{game_uuid}/calls", auth=(username, "secret"), data=call.json()
    )
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.call.assert_awaited_once()


@pytest.mark.parametrize(
    "error",
    [
        (bridgeprotocol.NotFoundError, fastapi.status.HTTP_404_NOT_FOUND),
        (bridgeprotocol.RuleViolationError, fastapi.status.HTTP_409_CONFLICT),
    ],
)
def test_make_call_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username, error
):
    exception_class, status_code = error
    call = models.Call(type=models.CallType.pass_)
    mock_bridge_client.call.side_effect = exception_class
    res = client.post(
        f"/api/v1/games/{game_uuid}/calls", auth=(username, "secret"), data=call.json()
    )
    assert res.status_code == status_code
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


def test_play_card_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    card = models.CardType(rank=models.Rank.seven, suit=models.Suit.diamonds)
    mock_bridge_client.play.side_effect = bridgeprotocol.NotFoundError
    res = client.post(
        f"/api/v1/games/{game_uuid}/trick", auth=(username, "secret"), data=card.json()
    )
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.play.assert_awaited_once()


@pytest.mark.parametrize(
    "error",
    [
        (bridgeprotocol.NotFoundError, fastapi.status.HTTP_404_NOT_FOUND),
        (bridgeprotocol.SeatReservedError, fastapi.status.HTTP_409_CONFLICT),
    ],
)
def test_play_card_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username, error
):
    exception_class, status_code = error
    card = models.CardType(rank=models.Rank.seven, suit=models.Suit.diamonds)
    mock_bridge_client.play.side_effect = exception_class
    res = client.post(
        f"/api/v1/games/{game_uuid}/trick", auth=(username, "secret"), data=card.json()
    )
    assert res.status_code == status_code
    mock_bridge_client.play.assert_awaited_once()


@pytest.mark.parametrize("event_type", ["turn", "call", "play"])
def test_games_websocket_should_return_events(
    client, mock_event_receiver, game_uuid, event_type
):
    event = bridgeprotocol.BridgeEvent(game=game_uuid, type=event_type)
    mock_event_receiver.get_event.side_effect = itertools.repeat(event)
    with client.websocket_connect(f"/api/v1/games/{game_uuid}/ws") as websocket:
        assert _receive_event_helper(websocket) == event
    mock_event_receiver.get_event.assert_awaited()


def test_games_websocket_should_return_multiple_events(
    client, mock_event_receiver, game_uuid
):
    events = [
        bridgeprotocol.BridgeEvent(game=game_uuid, type=event_type)
        for event_type in ["event1", "event2"]
    ]
    mock_event_receiver.get_event.side_effect = itertools.cycle(events)
    with client.websocket_connect(f"/api/v1/games/{game_uuid}/ws") as websocket:
        for event in events:
            assert _receive_event_helper(websocket) == event
    mock_event_receiver.get_event.assert_awaited()


def test_games_websocket_should_demultiplex_events_from_different_games(
    client, mock_event_receiver
):
    events = [
        bridgeprotocol.BridgeEvent(game=game_uuid, type="event")
        for game_uuid in [uuid.uuid4(), uuid.uuid4()]
    ]
    mock_event_receiver.get_event.side_effect = itertools.cycle(events)
    for event in events:
        with client.websocket_connect(f"/api/v1/games/{event.game}/ws") as websocket:
            assert _receive_event_helper(websocket) == event
    mock_event_receiver.get_event.assert_awaited()
