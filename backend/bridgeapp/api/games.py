"""
Games endpoints
...............
"""

import asyncio
import uuid
import typing

import fastapi
import orjson
import starlette.websockets as ws

from bridgeapp import models as base_models

from . import models, utils

COUNTER_HEADER = "X-Counter"
"""Header containing the running counter of game state"""

_GAME_NOT_FOUND_RESPONSE = {
    "model": models.Error,
    "description": "Game not found",
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
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=models.Game,
)
async def post_games(
    request: fastapi.Request,
    response: fastapi.Response,
    _credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(security),
):
    """
    This call causes a new game to be created. The server generates an UUID for
    the game and return it in the response body.
    """
    client = await utils.get_bridge_client()
    game_uuid = await client.game()
    response.headers["Location"] = request.url_for("game_details", game_uuid=game_uuid)
    return models.Game(uuid=game_uuid).dict(exclude_unset=True)


@router.get(
    "/{game_uuid}",
    name="game_details",
    summary="Get information about a game",
    description="""The response contains a representation of the game from the point of view of
    the authenticated player. If the player is not in the game, only public
    information will be retrieved.""",
    response_model=models.Game,
    responses={
        fastapi.status.HTTP_200_OK: {
            "headers": {
                COUNTER_HEADER: {
                    "schema": {"type": "integer"},
                    "description": "Running counter that can be used to synchronize event stream",
                }
            }
        },
        fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE,
    },
)
async def get_game_details(
    response: fastapi.Response,
    game_uuid: uuid.UUID,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting game details"""
    client = await utils.get_bridge_client()
    deal, counter = await client.get_deal(game=game_uuid, player=player_uuid)
    response.headers[COUNTER_HEADER] = str(counter)
    return models.Game(uuid=game_uuid, deal=deal)


@router.get(
    "/{game_uuid}/self",
    name="game_self",
    summary="Get information about the authenticated player",
    description="""The response contains information about the authenticated player itself
    within the game, including position and available moves.""",
    response_model=base_models.PlayerState,
    responses={fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE},
)
async def get_game_self(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid)
):
    """Handle getting self details"""
    client = await utils.get_bridge_client()
    return await client.get_self(game=game_uuid, player=player_uuid)


@router.get(
    "/{game_uuid}/results",
    name="game_results",
    summary="Get deal results of the game",
    description="""The response will contain an array of deal results in the chronological
    order.""",
    response_model=typing.List[base_models.DealResult],
    responses={fastapi.status.HTTP_404_NOT_FOUND: _GAME_NOT_FOUND_RESPONSE},
)
async def get_game_results(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid)
):
    del player_uuid
    client = await utils.get_bridge_client()
    return await client.get_results(game=game_uuid)


@router.get(
    "/{game_uuid}/players",
    name="game_players_list",
    summary="Get the players in a game",
    description="""Retrieve a mapping between positions and players in a game.""",
    response_model=base_models.PlayersInGame,
)
async def get_game_players(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle getting player details"""
    del player_uuid
    client = await utils.get_bridge_client()
    return await client.get_players(game=game_uuid)


@router.post(
    "/{game_uuid}/players",
    name="game_players",
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
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Handle adding player to a game"""
    client = await utils.get_bridge_client()
    await client.join(game=game_uuid, player=player_uuid)


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
    game_uuid: uuid.UUID, websocket: ws.WebSocket,
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
                    await websocket.send_bytes(
                        orjson.dumps(await event_task, default=dict)
                    )
                    event_task = _create_event_task()
                    pending.add(event_task)
                if recv_task in done:
                    await recv_task
                    recv_task = _create_recv_task()
                    pending.add(recv_task)
        except ws.WebSocketDisconnect:
            pass
        finally:
            event_task.cancel()
            recv_task.cancel()
            await websocket.close()
