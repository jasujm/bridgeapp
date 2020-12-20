"""
Players endpoints
.................
"""

import uuid

import fastapi

from . import models

router = fastapi.APIRouter()


@router.get(
    "/{player_id}",
    name="player_details",
    summary="Get infomation about a player",
    description="""This endpoint is a stub ensuring that each player has an URL.""",
    response_model=models.Player,
)
def get_player_details(request: fastapi.Request, player_id: uuid.UUID):
    """Handle getting player details"""
    del player_id
    return models.Player(self=str(request.url))
