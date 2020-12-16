"""
Players endpoints
.................
"""

import uuid

import fastapi

from . import models

router = fastapi.APIRouter()


@router.get(
    "/{player_uuid}",
    name="player_details",
    summary="Get infomation about a player",
    description="""This endpoint is a stub ensuring that each player has an URL.""",
    response_model=models.Player,
)
def get_player_details(request: fastapi.Request, player_uuid: uuid.UUID):
    """Handle getting player details"""
    del player_uuid
    return models.Player(self=str(request.url))
