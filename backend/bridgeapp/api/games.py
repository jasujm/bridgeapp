"""
Games endpoints
...............
"""

import asyncio
import uuid
import typing

import fastapi
import orjson

from bridgeapp.bridgeprotocol import models as base_models

from . import models, utils

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

router = fastapi.APIRouter()
security = fastapi.security.HTTPBasic()


def _get_player_uuid(
    credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(security),
):
    # TODO: Actually authenticate a player
    return utils.generate_player_uuid(credentials.username)


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
    _credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(security),
):
    """Handle creating a game"""
    client = await utils.get_bridge_client()
    game_uuid = await client.game()
    game_url = request.url_for("game_details", game_uuid=game_uuid)
    response.headers["Location"] = game_url
    return models.Game(self=game_url)


@router.get(
    "/{game_uuid}",
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
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting game details"""
    client = await utils.get_bridge_client()
    game, request.state.counter_header_value = await client.get_game(
        game=game_uuid, player=player_uuid
    )
    return models.Game(
        self=str(request.url),
        deal=models.Deal.from_base_model(game.deal, request),
        me=game.self,
        results=[
            models.DealResult.from_base_model(result, request)
            for result in game.results
        ],
        players=models.PlayersInGame.from_base_model(game.players, request),
    )


@router.get(
    "/{game_uuid}/deal",
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
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting the current deal of a game"""
    client = await utils.get_bridge_client()
    deal, request.state.counter_header_value = await client.get_deal(
        game=game_uuid, player=player_uuid
    )
    return models.Deal.from_base_model(deal, request)


@router.get(
    "/{game_uuid}/me",
    name="game_me",
    summary="Get information about the authenticated player",
    description="""The response contains information about the authenticated player itself
    within the game, including position and available moves.""",
    response_model=base_models.PlayerState,
    responses=_GAME_RESPONSES,
)
async def get_game_me(
    request: fastapi.Request,
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting self details"""
    client = await utils.get_bridge_client()
    me_, request.state.counter_header_value = await client.get_self(
        game=game_uuid, player=player_uuid
    )
    return me_


@router.get(
    "/{game_uuid}/results",
    name="game_results",
    summary="Get deal results of the game",
    description="""The response will contain an array of deal results in the chronological
    order.""",
    response_model=typing.List[models.DealResult],
    responses=_GAME_RESPONSES,
)
async def get_game_results(
    request: fastapi.Request,
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting deal results"""
    del player_uuid
    client = await utils.get_bridge_client()
    deal_results, request.state.counter_header_value = await client.get_results(
        game=game_uuid
    )
    return [
        models.DealResult.from_base_model(result, request) for result in deal_results
    ]


@router.get(
    "/{game_uuid}/players",
    name="game_players_list",
    summary="Get the players in a game",
    description="""Retrieve a mapping between positions and players in a game.""",
    response_model=models.PlayersInGame,
    responses=_GAME_RESPONSES,
)
async def get_game_players(
    request: fastapi.Request,
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting player details"""
    del player_uuid
    client = await utils.get_bridge_client()
    players_in_game, request.state.counter_header_value = await client.get_players(
        game=game_uuid
    )
    return models.PlayersInGame.from_base_model(players_in_game, request)


@router.post(
    "/{game_uuid}/players",
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
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
    position: typing.Optional[base_models.Position] = None,
):
    """Handle adding player to a game"""
    client = await utils.get_bridge_client()
    await client.join(game=game_uuid, player=player_uuid, position=position)


@router.delete(
    "/{game_uuid}/players",
    name="game_players_delete",
    summary="Remove a player from a game",
    description="""Make the authenticated player leave the game.""",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    responses={fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,},
)
async def delete_game_players(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle removing a player from a game"""
    client = await utils.get_bridge_client()
    await client.leave(game=game_uuid, player=player_uuid)


@router.post(
    "/{game_uuid}/calls",
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
    game_uuid: uuid.UUID,
    call: base_models.Call,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle adding call to a bidding"""
    client = await utils.get_bridge_client()
    await client.call(game=game_uuid, player=player_uuid, call=call)


@router.post(
    "/{game_uuid}/trick",
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
    game_uuid: uuid.UUID,
    card: base_models.CardType,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle adding card to a trick"""
    client = await utils.get_bridge_client()
    await client.play(game=game_uuid, player=player_uuid, card=card)


@router.websocket("/{game_uuid}/ws")
async def games_websocket(
    game_uuid: uuid.UUID, websocket: fastapi.WebSocket,
):
    """Open a websocket publishing events about a game"""
    loop = asyncio.get_running_loop()
    with utils.subscribe_events(game_uuid) as producer:

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
                    event = models.BridgeEvent.from_base_model(event, websocket)
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
