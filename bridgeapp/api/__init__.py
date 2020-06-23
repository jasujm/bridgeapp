"""
Bridge API definition
---------------------
"""

import uuid

import fastapi

from .. import models

from . import _bridgeprotocol

ROUTER_PREFIX = "/api/v1"

router = fastapi.APIRouter()


@router.on_event("startup")
async def _startup_event():
    await _bridgeprotocol.startup()


@router.on_event("shutdown")
def _shutdown_event():
    _bridgeprotocol.shutdown()


@router.post("/games", status_code=fastapi.status.HTTP_201_CREATED)
async def create_game(response: fastapi.Response) -> models.Game:
    """Create a new game"""
    client = _bridgeprotocol.get_client()
    game_uuid = await client.game()
    response.headers["Location"] = f"{ROUTER_PREFIX}/games/{game_uuid}"
    return models.Game(uuid=game_uuid)


@router.post(
    "/games/{game_uuid}/players", status_code=fastapi.status.HTTP_204_NO_CONTENT
)
async def add_player(game_uuid: uuid.UUID, player: models.Player):
    """Add a player to an existing game"""
    client = _bridgeprotocol.get_client()
    await client.join(game=game_uuid, player=player.uuid)
