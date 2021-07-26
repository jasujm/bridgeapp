"""
Games endpoints
...............
"""

import asyncio
import functools
import operator
import uuid
import typing

import fastapi
import elasticsearch_dsl.query as esq
import orjson
import pydantic
import sqlalchemy

from bridgeapp import db, search
from bridgeapp.bridgeprotocol import models as base_models

from . import auth, db_utils, models, search_utils, utils

COUNTER_HEADER = "X-Counter"
"""Header containing the running counter of game state"""

_GAME_NOT_FOUND_RESPONSE = {
    "model": models.Error,
    "description": "Game not found",
}

_GAME_OK_RESPONSE = {
    "headers": {
        COUNTER_HEADER: {
            "schema": {"type": "integer"},
            "description": "Running counter that can be used to synchronize event stream",
        }
    }
}

_GAME_RESPONSES = {
    fastapi.status.HTTP_200_OK: _GAME_OK_RESPONSE,
    fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,
}


async def _apify_players_in_game(
    players: base_models.PlayersInGame, request: fastapi.Request
):
    # This funky piece of code takes PlayersInGame (mapping between
    # positions and UUIDs) into apified PlayersInGameModel (mapping
    # between positions and actual player models)
    ids = [getattr(players, position.name) for position in base_models.Position]
    attrs = await db_utils.select(
        sqlalchemy.select([db.players]).where(db.players.c.id.in_(ids))
    )
    attrs_map = {attrs.id: attrs for attrs in attrs}
    return models.PlayersInGame(
        **{
            position.name: (
                (player := getattr(players, position.name, None))
                and models.Player.from_attributes(attrs_map[player].items(), request)
            )
            for position in base_models.Position
        },
    )


_ALL_SEATS_FILLED_QUERY = functools.reduce(
    operator.and_,
    (
        esq.Exists(field=f"players.{position.value}.id")
        for position in base_models.Position
    ),
)


def _get_games_search_query(q: str) -> esq.Q:
    return esq.Boosting(
        positive=esq.MultiMatch(query=q) & esq.Match(isPublic=True),
        negative=_ALL_SEATS_FILLED_QUERY,
        negative_boost=0.5,
    )


router = fastapi.APIRouter()


@router.post(
    "",
    name="games",
    summary="Create a new game",
    description="""Creates a new game. The server generates an UUID for the game and return it
    in the response body.""",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=models.Game,
)
async def post_games(
    request: fastapi.Request,
    response: fastapi.Response,
    game: models.GameCreate,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle creating a game"""
    del player
    client = await utils.get_bridge_client()
    game_id = await client.game()
    game_attrs = game.dict()
    with utils.autocancel_tasks() as create_task:
        game_db_create = create_task(db_utils.create(db.games, game_id, game_attrs))
        game_index = create_task(
            search_utils.index(search.GameSummary(id=game_id, **game_attrs), game_id)
        )
        await asyncio.gather(game_db_create, game_index)
    game_url = request.url_for("game_details", game_id=game_id)
    response.headers["Location"] = game_url
    return models.Game(id=game_id, self=game_url, **game_attrs)


@router.get(
    "",
    name="games_list",
    summary="List games",
    description="""Search games by a query string, and return summaries of the matched games.""",
    response_model=typing.List[models.GameSummary],
)
async def get_games_list(
    request: fastapi.Request,
    q: str = fastapi.Query(..., title="Query string"),
    limit: pydantic.conint(ge=1, le=1000) = fastapi.Query(10, title="Result limit"),
):
    """Handle listing games"""
    games = await search_utils.search(
        search.GameSummary, _get_games_search_query(q), limit=limit
    )
    games_attrs = []
    for game in games:
        game = game.to_dict()
        players = game.get("players", {})
        for position in list(players.keys()):
            players[position] = models.Player.from_attributes(
                players[position].items(), request
            )
        games_attrs.append(game)
    return [
        models.GameSummary.from_attributes(attrs.items(), request)
        for attrs in games_attrs
    ]


@router.get(
    "/{game_id}",
    name="game_details",
    summary="Get information about a game",
    description="""The response contains a representation of the game from the point of view of
    the authenticated player. If the player is not in the game, only public
    information will be retrieved.""",
    response_model=models.Game,
    responses=_GAME_RESPONSES,
)
async def get_game_details(
    request: fastapi.Request,
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting game details"""
    with utils.autocancel_tasks() as create_task:
        game_attrs_load = create_task(db_utils.load(db.games, game_id))
        client = await utils.get_bridge_client()
        game, request.state.counter_header_value = await client.get_game(
            game=game_id, player=player.id
        )
        players_load = create_task(_apify_players_in_game(game.players, request))
        game_attrs, players = await asyncio.gather(game_attrs_load, players_load)
    return models.Game(
        **game_attrs,
        self=str(request.url),
        deal=models.Deal.from_attributes(game.deal, request),
        me=game.self,
        results=[
            models.DealResult.from_attributes(result, request)
            for result in game.results
        ],
        players=players,
    )


@router.get(
    "/{game_id}/deal",
    name="game_deal",
    summary="Get the current deal of a game",
    description="""The response contains a representation of the current deal of the game from
    the point of view of the authenticated player. If the player is not in the
    game, only public information will be retrieved.""",
    response_model=models.Deal,
    responses=_GAME_RESPONSES,
)
async def get_game_deal(
    request: fastapi.Request,
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting the current deal of a game"""
    client = await utils.get_bridge_client()
    deal, request.state.counter_header_value = await client.get_game_deal(
        game=game_id, player=player.id
    )
    return models.Deal.from_attributes(deal, request)


@router.get(
    "/{game_id}/me",
    name="game_me",
    summary="Get information about the authenticated player",
    description="""The response contains information about the authenticated player itself
    within the game, including position and available moves.""",
    response_model=base_models.PlayerState,
    responses=_GAME_RESPONSES,
)
async def get_game_me(
    request: fastapi.Request,
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting self details"""
    client = await utils.get_bridge_client()
    me_, request.state.counter_header_value = await client.get_self(
        game=game_id, player=player.id
    )
    return me_


@router.get(
    "/{game_id}/results",
    name="game_results",
    summary="Get deal results of the game",
    description="""The response will contain an array of deal results in the chronological
    order.""",
    response_model=typing.List[models.DealResult],
    responses=_GAME_RESPONSES,
)
async def get_game_results(
    request: fastapi.Request,
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting deal results"""
    del player
    client = await utils.get_bridge_client()
    deal_results, request.state.counter_header_value = await client.get_results(
        game=game_id
    )
    return [
        models.DealResult.from_attributes(result, request) for result in deal_results
    ]


@router.get(
    "/{game_id}/players",
    name="game_players_list",
    summary="Get the players in a game",
    description="""Retrieve a mapping between positions and players in a game.""",
    response_model=models.PlayersInGame,
    responses=_GAME_RESPONSES,
)
async def get_game_players(
    request: fastapi.Request,
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting player details"""
    del player
    client = await utils.get_bridge_client()
    players, request.state.counter_header_value = await client.get_players(game=game_id)
    return await _apify_players_in_game(players, request)


@router.post(
    "/{game_id}/players",
    name="game_players_create",
    summary="Add a player to a game",
    description="""Make the authenticated player join the game, if there are seats available.""",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,
        fastapi.status.HTTP_409_CONFLICT: {
            "model": models.Error,
            "description": "Cannot join the game",
        },
    },
)
async def post_game_players(
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
    position: typing.Optional[base_models.Position] = None,
):
    """Handle adding player to a game"""
    client = await utils.get_bridge_client()
    game_id, position = await client.join(
        game=game_id, player=player.id, position=position
    )
    player = dict(**player)
    del player["password"]
    await search_utils.update(
        search.GameSummary(
            players=search.PlayersInGame(**{position.value: search.Player(**player)})
        ),
        game_id,
    )


@router.delete(
    "/{game_id}/players",
    name="game_players_delete",
    summary="Remove a player from a game",
    description="""Make the authenticated player leave the game.""",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,},
)
async def delete_game_players(
    game_id: uuid.UUID,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle removing a player from a game"""
    client = await utils.get_bridge_client()
    position = await client.leave(game=game_id, player=player.id)
    if position:
        await search_utils.remove(
            search.GameSummary, game_id, ["players", position.value]
        )


@router.post(
    "/{game_id}/calls",
    name="game_calls",
    summary="Add a call to the current bidding",
    description="""Make a call as the authenticated player. Making call is only possible during
    the bidding phase of a deal, if the player has turn, and the call is
    legal.""",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,
        fastapi.status.HTTP_409_CONFLICT: {
            "model": models.Error,
            "description": "Making the call would violate the rules",
        },
    },
)
async def post_game_calls(
    game_id: uuid.UUID,
    call: base_models.Call,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle adding call to a bidding"""
    client = await utils.get_bridge_client()
    await client.call(game=game_id, player=player.id, call=call)


@router.post(
    "/{game_id}/trick",
    name="game_trick",
    summary="Add a card to the current trick",
    description="""Play a card the authenticated player. Playing card is only possible possible
    during the playing phase of a deal, if the player has turn, and playing the
    card is legal.""",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,
        fastapi.status.HTTP_409_CONFLICT: {
            "model": models.Error,
            "description": "Playing the card would violate the rules",
        },
    },
)
async def post_game_trick(
    game_id: uuid.UUID,
    card: base_models.CardType,
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle adding card to a trick"""
    client = await utils.get_bridge_client()
    await client.play(game=game_id, player=player.id, card=card)


@router.websocket("/{game_id}/ws")
async def games_websocket(
    game_id: uuid.UUID, websocket: fastapi.WebSocket,
):
    """Open a websocket publishing events about a game"""
    loop = asyncio.get_running_loop()
    with utils.subscribe_events(game_id) as producer:

        def _create_event_task():
            return loop.create_task(producer.get_event())

        def _create_recv_task():
            return loop.create_task(websocket.receive_bytes())

        await websocket.accept()
        event_task = _create_event_task()
        recv_task = _create_recv_task()
        pending = {event_task, recv_task}
        try:
            while True:
                done, pending = await asyncio.wait(
                    pending, return_when=asyncio.FIRST_COMPLETED
                )
                if event_task in done:
                    event = await event_task
                    event = models.BridgeEvent.from_attributes(event, websocket)
                    await websocket.send_bytes(orjson.dumps(event, default=dict))
                    event_task = _create_event_task()
                    pending.add(event_task)
                if recv_task in done:
                    await recv_task
                    recv_task = _create_recv_task()
                    pending.add(recv_task)
        except fastapi.websockets.WebSocketDisconnect:
            pass
        finally:
            event_task.cancel()
            recv_task.cancel()
            await websocket.close()
