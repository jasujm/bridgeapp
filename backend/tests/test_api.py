"""
Tests for the :mod:`bridgeapp.api` module
"""

import itertools
import unittest.mock
import uuid

import fastapi
import fastapi.testclient
import pytest

from bridgeapp import application as app, api, bridgeprotocol

from bridgeapp.bridgeprotocol import models, events


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
        leave=unittest.mock.AsyncMock(),
        get_game=unittest.mock.AsyncMock(),
        get_deal=unittest.mock.AsyncMock(),
        get_self=unittest.mock.AsyncMock(),
        get_results=unittest.mock.AsyncMock(),
        get_players=unittest.mock.AsyncMock(),
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
    return api.models.BridgeEvent(**websocket.receive_json(mode="binary"))


def _get_event(game_uuid, event_type):
    return api.models.BridgeEvent(
        game=f"http://testserver/api/v1/games/{game_uuid}", type=event_type
    )


def test_generate_player_uuid():
    assert isinstance(api.utils.generate_player_uuid("username"), uuid.UUID)


def test_create_game(client, mock_bridge_client, game_uuid, username):
    mock_bridge_client.game.return_value = game_uuid
    res = client.post("/api/v1/games", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    game_url = f"http://testserver/api/v1/games/{game_uuid}"
    assert res.headers["Location"] == game_url
    assert api.models.Game(**res.json()) == api.models.Game(self=game_url)


def test_read_game(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    deal = models.Deal()
    api_deal = api.models.Deal(self=f"http://testserver/api/v1/deals/{deal.uuid}")
    game = models.Game(uuid=game_uuid, deal=deal)
    api_game = api.models.Game(
        self=f"http://testserver/api/v1/games/{game_uuid}", deal=api_deal,
    )
    mock_bridge_client.get_game.return_value = (game, 123)
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert res.headers[api.games.COUNTER_HEADER] == "123"
    assert api.models.Game(**res.json()) == api_game
    mock_bridge_client.get_game.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_read_game_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_game.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_game.assert_awaited_once()


def test_read_deal(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    deal = models.Deal()
    api_deal = api.models.Deal(self=f"http://testserver/api/v1/deals/{deal.uuid}")
    mock_bridge_client.get_deal.return_value = (deal, 123)
    res = client.get(f"/api/v1/games/{game_uuid}/deal", auth=(username, "secret"))
    assert res.headers[api.games.COUNTER_HEADER] == "123"
    assert api.models.Deal(**res.json()) == api_deal
    mock_bridge_client.get_deal.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_read_deal_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_deal.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}/deal", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_deal.assert_awaited_once()


def test_read_self(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    player_state = models.PlayerState(position=models.Position.north)
    mock_bridge_client.get_self.return_value = (player_state, 123)
    res = client.get(f"/api/v1/games/{game_uuid}/me", auth=(username, "secret"))
    assert models.PlayerState(**res.json()) == player_state
    mock_bridge_client.get_self.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_read_self_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_self.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}/me", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_self.assert_awaited_once()


def test_read_results(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    deal_results = [
        models.DealResult(
            deal=uuid.uuid4(),
            result=models.DuplicateResult(
                partnership=models.Partnership.eastWest, score=420
            ),
        )
    ]
    mock_bridge_client.get_results.return_value = (deal_results, 123)
    res = client.get(f"/api/v1/games/{game_uuid}/results", auth=(username, "secret"))
    assert res.json() == [
        {
            "deal": f"http://testserver/api/v1/deals/{deal_results[0].deal}",
            "result": {"partnership": "eastWest", "score": 420},
        }
    ]
    mock_bridge_client.get_results.assert_awaited_once_with(game=game_uuid)


def test_read_results_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_results.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}/results", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_results.assert_awaited_once()


def test_read_players(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    players_in_game = models.PlayersInGame(north=player_uuid)
    mock_bridge_client.get_players.return_value = (players_in_game, 123)
    res = client.get(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.json() == {
        "north": f"http://testserver/api/v1/players/{player_uuid}",
        "east": None,
        "south": None,
        "west": None,
    }
    mock_bridge_client.get_players.assert_awaited_once_with(game=game_uuid)


def test_read_players_should_fail_if_game_not_found(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.get_players.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_players.assert_awaited_once()


def test_add_player(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    res = client.post(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(
        game=game_uuid, player=player_uuid, position=None
    )


@pytest.mark.parametrize("position", list(models.Position))
def test_add_player_with_position(
    client, mock_bridge_client, game_uuid, username_and_player_uuid, position
):
    username, player_uuid = username_and_player_uuid
    res = client.post(
        f"/api/v1/games/{game_uuid}/players",
        params={"position": position.value},
        auth=(username, "secret"),
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(
        game=game_uuid, player=player_uuid, position=position
    )


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


def test_remove_player(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    res = client.delete(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.leave.assert_awaited_once_with(
        game=game_uuid, player=player_uuid
    )


def test_remove_player_should_fail_if_backend_fails(
    client, mock_bridge_client, game_uuid, username
):
    mock_bridge_client.leave.side_effect = bridgeprotocol.NotFoundError
    res = client.delete(f"/api/v1/games/{game_uuid}/players", auth=(username, "secret"))
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.leave.assert_awaited_once()


def test_make_call(client, mock_bridge_client, game_uuid, username_and_player_uuid):
    username, player_uuid = username_and_player_uuid
    call = models.Call(
        type=models.CallType.bid, bid=models.Bid(level=4, strain=models.Strain.spades)
    )
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
    event = events.BridgeEvent(game=game_uuid, type=event_type)
    mock_event_receiver.get_event.side_effect = itertools.repeat(event)
    with client.websocket_connect(f"/api/v1/games/{game_uuid}/ws") as websocket:
        assert _receive_event_helper(websocket) == _get_event(game_uuid, event_type)
    mock_event_receiver.get_event.assert_awaited()


def test_games_websocket_should_return_multiple_events(
    client, mock_event_receiver, game_uuid
):
    events_ = [
        events.BridgeEvent(game=game_uuid, type=event_type)
        for event_type in ["event1", "event2"]
    ]
    mock_event_receiver.get_event.side_effect = itertools.cycle(events_)
    with client.websocket_connect(f"/api/v1/games/{game_uuid}/ws") as websocket:
        for event in events_:
            assert _receive_event_helper(websocket) == _get_event(game_uuid, event.type)
    mock_event_receiver.get_event.assert_awaited()


def test_games_websocket_should_demultiplex_events_from_different_games(
    client, mock_event_receiver
):
    events_ = [
        events.BridgeEvent(game=game_uuid, type="event")
        for game_uuid in [uuid.uuid4(), uuid.uuid4()]
    ]
    mock_event_receiver.get_event.side_effect = itertools.cycle(events_)
    for event in events_:
        with client.websocket_connect(f"/api/v1/games/{event.game}/ws") as websocket:
            assert _receive_event_helper(websocket) == _get_event(event.game, "event")
    mock_event_receiver.get_event.assert_awaited()
