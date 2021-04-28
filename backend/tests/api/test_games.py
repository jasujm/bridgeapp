"""
Tests for the :mod:`bridgeapp.api` module
"""

import asyncio
import itertools
import unittest.mock
import uuid

import fastapi
import fastapi.testclient
import pytest

from bridgeapp import api, bridgeprotocol, db, search
from bridgeapp.api import db_utils as dbu

from bridgeapp.bridgeprotocol import models, events


@pytest.fixture
def mock_bridge_client(monkeypatch):
    """Yield mock client"""
    mock = unittest.mock.Mock(
        game=unittest.mock.AsyncMock(),
        join=unittest.mock.AsyncMock(),
        leave=unittest.mock.AsyncMock(),
        get_game=unittest.mock.AsyncMock(),
        get_game_deal=unittest.mock.AsyncMock(),
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


def _receive_event_helper(websocket):
    return api.models.BridgeEvent(**websocket.receive_json(mode="binary"))


def _get_event(game_id, event_type):
    return api.models.BridgeEvent(
        game=f"http://testserver/api/v1/games/{game_id}", type=event_type
    )


def test_list_games_no_result(client, credentials, mock_search):
    mock_search.search.return_value = []
    res = client.get("/api/v1/games", auth=credentials, params={"q": "nothing"})
    assert res.status_code == fastapi.status.HTTP_200_OK
    assert res.json() == []
    mock_search.search.assert_awaited_once_with(search.GameSummary, "nothing")


def test_list_games_with_result(
    client, game_id, player_id, username, credentials, mock_search
):
    mock_search.search.return_value = [
        search.GameSummary(
            id=game_id,
            name="hello",
            players=search.PlayersInGame(
                north=search.Player(id=player_id, username=username,),
            ),
        )
    ]
    res = client.get("/api/v1/games", auth=credentials, params={"q": "hello"})
    assert res.status_code == fastapi.status.HTTP_200_OK
    j = res.json()
    assert len(j) == 1
    assert api.models.Game(**j[0]) == api.models.Game(
        id=game_id,
        self=f"http://testserver/api/v1/games/{game_id}",
        name="hello",
        players=api.models.PlayersInGame(
            north=api.models.Player(
                id=player_id,
                self=f"http://testserver/api/v1/players/{player_id}",
                username=username,
            ),
        ),
    )
    mock_search.search.assert_awaited_once_with(search.GameSummary, "hello")


@pytest.mark.parametrize("name", ["my game", "other game"])
def test_create_game(
    client, mock_bridge_client, game_id, name, credentials, database, mock_search
):
    mock_bridge_client.game.return_value = game_id
    game_create = api.models.GameCreate(name=name)
    res = client.post("/api/v1/games", auth=credentials, json=game_create.dict())
    assert res.status_code == fastapi.status.HTTP_201_CREATED
    game_url = f"http://testserver/api/v1/games/{game_id}"
    assert res.headers["Location"] == game_url
    assert api.models.Game(**res.json()) == api.models.Game(
        id=game_id, self=game_url, name=name
    )
    game_in_db = asyncio.run(dbu.load(db.games, game_id, database=database))
    assert game_in_db.name == name
    mock_search.index.assert_awaited_once_with(
        search.GameSummary(id=game_id, name=name), game_id
    )


def test_read_game(
    client, mock_bridge_client, game_id, db_game, player_id, username, credentials
):
    deal = models.Deal()
    api_deal = api.models.Deal(
        id=deal.id, self=f"http://testserver/api/v1/deals/{deal.id}"
    )
    game = models.Game(
        id=game_id, deal=deal, players=models.PlayersInGame(north=player_id)
    )
    api_game = api.models.Game(
        id=game_id,
        self=f"http://testserver/api/v1/games/{game_id}",
        name=db_game,
        deal=api_deal,
        players=api.models.PlayersInGame(
            north=api.models.Player(
                id=player_id,
                self=f"http://testserver/api/v1/players/{player_id}",
                username=username,
            )
        ),
    )
    mock_bridge_client.get_game.return_value = (game, 123)
    res = client.get(f"/api/v1/games/{game_id}", auth=credentials)
    assert res.headers[api.games.COUNTER_HEADER] == "123"
    assert api.models.Game(**res.json()) == api_game
    mock_bridge_client.get_game.assert_awaited_once_with(game=game_id, player=player_id)


def test_read_game_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials, database
):
    mock_bridge_client.get_game.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_id}", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_game.assert_awaited_once()


def test_read_game_deal(
    client, mock_bridge_client, game_id, db_game, player_id, credentials
):
    deal = models.Deal()
    api_deal = api.models.Deal(
        id=deal.id, self=f"http://testserver/api/v1/deals/{deal.id}"
    )
    mock_bridge_client.get_game_deal.return_value = (deal, 123)
    res = client.get(f"/api/v1/games/{game_id}/deal", auth=credentials)
    assert res.headers[api.games.COUNTER_HEADER] == "123"
    assert api.models.Deal(**res.json()) == api_deal
    mock_bridge_client.get_game_deal.assert_awaited_once_with(
        game=game_id, player=player_id
    )


def test_read_game_deal_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials, database
):
    mock_bridge_client.get_game_deal.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_id}/deal", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_game_deal.assert_awaited_once()


def test_read_deal(client, mock_bridge_client):
    deal = models.Deal()
    api_deal = api.models.Deal(
        id=deal.id, self=f"http://testserver/api/v1/deals/{deal.id}"
    )
    mock_bridge_client.get_deal.return_value = deal
    res = client.get(f"/api/v1/deals/{deal.id}")
    assert api.models.Deal(**res.json()) == api_deal
    mock_bridge_client.get_deal.assert_awaited_once_with(deal=deal.id)


def test_read_deal_should_fail_if_deal_not_found(client, mock_bridge_client):
    mock_bridge_client.get_deal.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/deals/{uuid.uuid4()}")
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_deal.assert_awaited_once()


def test_read_self(client, mock_bridge_client, game_id, player_id, credentials):
    player_state = models.PlayerState(position=models.Position.north)
    mock_bridge_client.get_self.return_value = (player_state, 123)
    res = client.get(f"/api/v1/games/{game_id}/me", auth=credentials)
    assert models.PlayerState(**res.json()) == player_state
    mock_bridge_client.get_self.assert_awaited_once_with(game=game_id, player=player_id)


def test_read_self_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials
):
    mock_bridge_client.get_self.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_id}/me", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_self.assert_awaited_once()


def test_read_results(client, mock_bridge_client, game_id, credentials):
    deal_results = [
        models.DealResult(
            deal=uuid.uuid4(),
            result=models.DuplicateResult(
                partnership=models.Partnership.eastWest, score=420
            ),
        )
    ]
    mock_bridge_client.get_results.return_value = (deal_results, 123)
    res = client.get(f"/api/v1/games/{game_id}/results", auth=credentials)
    assert res.json() == [
        {
            "deal": f"http://testserver/api/v1/deals/{deal_results[0].deal}",
            "result": {"partnership": "eastWest", "score": 420},
        }
    ]
    mock_bridge_client.get_results.assert_awaited_once_with(game=game_id)


def test_read_results_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials
):
    mock_bridge_client.get_results.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_id}/results", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_results.assert_awaited_once()


def test_read_players(
    client, mock_bridge_client, game_id, player_id, username, credentials
):
    players_in_game = models.PlayersInGame(north=player_id)
    mock_bridge_client.get_players.return_value = (players_in_game, 123)
    res = client.get(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.json() == {
        "north": {
            "id": str(player_id),
            "self": f"http://testserver/api/v1/players/{player_id}",
            "username": username,
        },
        "east": None,
        "south": None,
        "west": None,
    }
    mock_bridge_client.get_players.assert_awaited_once_with(game=game_id)


def test_read_players_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials
):
    mock_bridge_client.get_players.side_effect = bridgeprotocol.NotFoundError
    res = client.get(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.get_players.assert_awaited_once()


def test_add_player(
    client, mock_bridge_client, game_id, player_id, username, credentials, mock_search
):
    mock_bridge_client.join.return_value = (game_id, models.Position.north)
    res = client.post(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(
        game=game_id, player=player_id, position=None
    )
    mock_search.update.assert_awaited_once_with(
        search.GameSummary(
            players=search.PlayersInGame(
                north=search.Player(id=player_id, username=username),
            )
        ),
        game_id,
    )


@pytest.mark.parametrize("position", list(models.Position))
def test_add_player_with_position(
    client,
    mock_bridge_client,
    game_id,
    player_id,
    username,
    credentials,
    position,
    mock_search,
):
    mock_bridge_client.join.return_value = (game_id, position)
    res = client.post(
        f"/api/v1/games/{game_id}/players",
        params={"position": position.value},
        auth=credentials,
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.join.assert_awaited_once_with(
        game=game_id, player=player_id, position=position
    )
    mock_search.update.assert_awaited_once_with(
        search.GameSummary(
            players=search.PlayersInGame(
                **{position.value: search.Player(id=player_id, username=username)},
            )
        ),
        game_id,
    )


@pytest.mark.parametrize(
    "error",
    [
        (bridgeprotocol.NotFoundError, fastapi.status.HTTP_404_NOT_FOUND),
        (bridgeprotocol.SeatReservedError, fastapi.status.HTTP_409_CONFLICT),
    ],
)
def test_add_player_should_fail_if_backend_fails(
    client, mock_bridge_client, game_id, credentials, error, mock_search
):
    exception_class, status_code = error
    mock_bridge_client.join.side_effect = exception_class
    res = client.post(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.status_code == status_code
    mock_bridge_client.join.assert_awaited_once()
    mock_search.update.assert_not_awaited()


def test_remove_player_not_in_game(
    client, mock_bridge_client, game_id, player_id, credentials, mock_search
):
    mock_bridge_client.leave.return_value = None
    res = client.delete(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.leave.assert_awaited_once_with(game=game_id, player=player_id)
    mock_search.remove.assert_not_awaited()


@pytest.mark.parametrize("position", list(models.Position))
def test_remove_player(
    client, mock_bridge_client, game_id, player_id, credentials, mock_search, position
):
    mock_bridge_client.leave.return_value = position
    res = client.delete(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.leave.assert_awaited_once_with(game=game_id, player=player_id)
    mock_search.remove.assert_awaited_once_with(
        search.GameSummary, game_id, ["players", position.value]
    )


def test_remove_player_should_fail_if_backend_fails(
    client, mock_bridge_client, game_id, credentials, mock_search
):
    mock_bridge_client.leave.side_effect = bridgeprotocol.NotFoundError
    res = client.delete(f"/api/v1/games/{game_id}/players", auth=credentials)
    assert res.status_code == fastapi.status.HTTP_404_NOT_FOUND
    mock_bridge_client.leave.assert_awaited_once()
    mock_search.remove.assert_not_awaited()


def test_make_call(client, mock_bridge_client, game_id, player_id, credentials):
    call = models.Call(
        type=models.CallType.bid, bid=models.Bid(level=4, strain=models.Strain.spades)
    )
    res = client.post(
        f"/api/v1/games/{game_id}/calls", auth=credentials, data=call.json(),
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.call.assert_awaited_once_with(
        game=game_id, player=player_id, call=call
    )


def test_make_call_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials
):
    call = models.Call(type=models.CallType.pass_)
    mock_bridge_client.call.side_effect = bridgeprotocol.NotFoundError
    res = client.post(
        f"/api/v1/games/{game_id}/calls", auth=credentials, data=call.json(),
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
    client, mock_bridge_client, game_id, credentials, error
):
    exception_class, status_code = error
    call = models.Call(type=models.CallType.pass_)
    mock_bridge_client.call.side_effect = exception_class
    res = client.post(
        f"/api/v1/games/{game_id}/calls", auth=credentials, data=call.json(),
    )
    assert res.status_code == status_code
    mock_bridge_client.call.assert_awaited_once()


def test_play_card(client, mock_bridge_client, game_id, player_id, credentials):
    card = models.CardType(rank=models.Rank.queen, suit=models.Suit.hearts)
    res = client.post(
        f"/api/v1/games/{game_id}/trick", auth=credentials, data=card.json(),
    )
    assert res.status_code == fastapi.status.HTTP_204_NO_CONTENT
    mock_bridge_client.play.assert_awaited_once_with(
        game=game_id, player=player_id, card=card
    )


def test_play_card_should_fail_if_game_not_found(
    client, mock_bridge_client, game_id, credentials
):
    card = models.CardType(rank=models.Rank.seven, suit=models.Suit.diamonds)
    mock_bridge_client.play.side_effect = bridgeprotocol.NotFoundError
    res = client.post(
        f"/api/v1/games/{game_id}/trick", auth=credentials, data=card.json(),
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
    client, mock_bridge_client, game_id, credentials, error
):
    exception_class, status_code = error
    card = models.CardType(rank=models.Rank.seven, suit=models.Suit.diamonds)
    mock_bridge_client.play.side_effect = exception_class
    res = client.post(
        f"/api/v1/games/{game_id}/trick", auth=credentials, data=card.json(),
    )
    assert res.status_code == status_code
    mock_bridge_client.play.assert_awaited_once()


@pytest.mark.parametrize("event_type", ["turn", "call", "play"])
def test_games_websocket_should_return_events(
    client, mock_event_receiver, game_id, event_type
):
    event = events.BridgeEvent(game=game_id, type=event_type)
    mock_event_receiver.get_event.side_effect = itertools.repeat(event)
    with client.websocket_connect(f"/api/v1/games/{game_id}/ws") as websocket:
        assert _receive_event_helper(websocket) == _get_event(game_id, event_type)
    mock_event_receiver.get_event.assert_awaited()


def test_games_websocket_should_return_multiple_events(
    client, mock_event_receiver, game_id
):
    events_ = [
        events.BridgeEvent(game=game_id, type=event_type)
        for event_type in ["event1", "event2"]
    ]
    mock_event_receiver.get_event.side_effect = itertools.cycle(events_)
    with client.websocket_connect(f"/api/v1/games/{game_id}/ws") as websocket:
        for event in events_:
            assert _receive_event_helper(websocket) == _get_event(game_id, event.type)
    mock_event_receiver.get_event.assert_awaited()


def test_games_websocket_should_demultiplex_events_from_different_games(
    client, mock_event_receiver
):
    events_ = [
        events.BridgeEvent(game=game_id, type="event")
        for game_id in [uuid.uuid4(), uuid.uuid4()]
    ]
    mock_event_receiver.get_event.side_effect = itertools.cycle(events_)
    for event in events_:
        with client.websocket_connect(f"/api/v1/games/{event.game}/ws") as websocket:
            assert _receive_event_helper(websocket) == _get_event(event.game, "event")
    mock_event_receiver.get_event.assert_awaited()
