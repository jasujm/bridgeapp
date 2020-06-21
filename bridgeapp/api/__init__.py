"""
Bridge API definition
---------------------
"""

import uuid

from fastapi import APIRouter, Header, Depends, Response, status

from .. import models

from . import _bridgeprotocol

router = APIRouter()


@router.on_event("startup")
async def _startup_event():
    await _bridgeprotocol.startup()


@router.on_event("shutdown")
def _shutdown_event():
    _bridgeprotocol.shutdown()


@router.post("/games", status_code=status.HTTP_201_CREATED)
async def create_game() -> models.Game:
    """Create a new game"""
    client = _bridgeprotocol.get_client()
    game_uuid = await client.game()
    return models.Game(uuid=game_uuid)


@router.post("/games/{game_uuid}/players", status_code=status.HTTP_204_NO_CONTENT)
async def add_player(
    game_uuid: uuid.UUID, player: models.Player
):
    """Add a player to an existing game"""
    client = _bridgeprotocol.get_client()
    await client.join(game=game_uuid, player=player.uuid
)
