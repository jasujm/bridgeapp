"""
Players endpoints
.................
"""

import uuid

import fastapi

from . import models, db_utils as dbu
from .. import db

router = fastapi.APIRouter()


@router.post(
    "",
    name="players",
    summary="Create new player",
    description="""Creates a new player (user) that can be used to authenticate and play
    bridge. The server assigns the new player an identity and returns it with
    the response.""",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=models.Player,
)
async def post_players(
    request: fastapi.Request, response: fastapi.Response, player: models.PlayerCreate
):
    """Handle creating a new player"""
    player_id = uuid.uuid4()
    player_url = request.url_for("player_details", player_id=player_id)
    player_attrs = player.dict()
    await dbu.create(db.players, player_id, player_attrs)
    response.headers["Location"] = player_url
    return models.Player(id=player_id, self=player_url, **player_attrs)


@router.get(
    "/{player_id}",
    name="player_details",
    summary="Get infomation about a player",
    description="""Returns information about the player identified by ``player_id``.""",
    response_model=models.Player,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {
            "model": models.Error,
            "description": "Player not found",
        },
    },
)
async def get_player_details(request: fastapi.Request, player_id: uuid.UUID):
    """Handle getting player details"""
    player_attrs = await dbu.load(db.players, player_id)
    return models.Player(**player_attrs, self=str(request.url))
