"""
Players endpoints
.................
"""

import uuid
import typing

import fastapi

from bridgeapp import db

from . import models, db_utils as dbu, auth

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
    responses={
        fastapi.status.HTTP_409_CONFLICT: {
            "model": models.Error,
            "description": "Player with the given username already exists",
        }
    },
)
async def post_players(
    request: fastapi.Request, response: fastapi.Response, player: models.PlayerCreate
):
    """Handle creating a new player"""
    player_id = uuid.uuid4()
    player_url = request.url_for("player_details", id=player_id)
    player_attrs = player.dict()
    player_attrs["password"] = player.password.get_secret_value()
    try:
        await dbu.create(db.players, player_id, player_attrs)
    except dbu.AlreadyExistsError as ex:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_409_CONFLICT,
            detail="Player already exists",
        ) from ex
    response.headers["Location"] = player_url
    return {"id": player_id, **player_attrs}


@router.get(
    "/me",
    name="player_self",
    summary="Get information about the authenticated player",
    description="""Returns information about the authenticated player.""",
    response_model=models.Player,
)
async def get_player_self(
    player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting authenticated player"""
    return player


@router.patch(
    "/me",
    name="player_self_update",
    summary="Update the attributes of the authenticated player",
    description="""Updates the attributes of the authenticated player to the new attributes
    given in the body. Attributes may be omitted, in which case they are left
    intact.""",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def patch_player_self(
    player: models.PlayerUpdate,
    authenticated_player: uuid.UUID = fastapi.Depends(auth.get_authenticated_player),
):
    """Handle getting authenticated player"""
    player_attrs = player.dict(exclude_unset=True)
    if player.password:
        player_attrs["password"] = player.password.get_secret_value()
    await dbu.update(db.players, authenticated_player.id, player_attrs)


@router.get(
    "/{id}",
    name="player_details",
    summary="Get infomation about a player",
    description="""Returns information about the player identified by ``id``. The
    parameter is either the ID or the username of the player.""",
    response_model=models.Player,
    responses={
        fastapi.status.HTTP_404_NOT_FOUND: {
            "model": models.Error,
            "description": "Player not found",
        },
    },
)
async def get_player_details(id: typing.Union[uuid.UUID, models.Username]):
    """Handle getting player details"""
    key = db.players.c.id if isinstance(id, uuid.UUID) else db.players.c.username
    player_attrs = await dbu.load(db.players, id, key=key)
    return player_attrs
