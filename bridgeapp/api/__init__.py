"""
Bridge API definition
---------------------
"""

import uuid

import fastapi

from bridgeapp import models, settings

from . import _bridgeprotocol, utils

ROUTER_PREFIX = "/api/v1"

router = fastapi.APIRouter()
security = fastapi.security.HTTPBasic()


def _get_player_uuid(
    credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(security),
):
    # TODO: Actually authenticate a player
    return utils.generate_player_uuid(credentials.username)


@router.post(
    "/games", status_code=fastapi.status.HTTP_201_CREATED, summary="Create a new game"
)
async def create_game(response: fastapi.Response) -> models.Game:
    """Create a new game

    This call causes a new game to be created. The server SHALL
    generate an UUID for the game and return it in the response
    body.
    """
    client = _bridgeprotocol.get_client()
    game_uuid = await client.game()
    response.headers["Location"] = f"{ROUTER_PREFIX}/games/{game_uuid}"
    return models.Game(uuid=game_uuid)


@router.post(
    "/games/{game_uuid}/players",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
    summary="Add a player to a game",
)
async def add_player(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """Add a player to an existing game

    This call causes the authenticated user to be added as a player to
    the game identified by ``game_uuid``.
    """
    client = _bridgeprotocol.get_client()
    await client.join(game=game_uuid, player=player_uuid)


@router.on_event("startup")
async def _startup_event():
    await _bridgeprotocol.startup()


@router.on_event("shutdown")
def _shutdown_event():
    _bridgeprotocol.shutdown()
