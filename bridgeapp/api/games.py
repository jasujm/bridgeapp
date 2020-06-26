"""
Bridge API games endpoints
--------------------------
"""

import uuid

import fastapi

from . import models, utils

router = fastapi.APIRouter()
security = fastapi.security.HTTPBasic()

# API calls are documented in the fastapi style
# pylint: disable=missing-function-docstring

def _get_player_uuid(
    credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(security),
):
    # TODO: Actually authenticate a player
    return utils.generate_player_uuid(credentials.username)


@router.post(
    "",
    name="games_list",
    summary="Create a new game",
    status_code=fastapi.status.HTTP_201_CREATED,
    response_model=models.Game,
)
async def games_list(
    request: fastapi.Request,
    response: fastapi.Response,
    _credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(security),
):
    """
    This call causes a new game to be created. The server SHALL generate an UUID
    for the game and return it in the response body.
    """
    client = utils.get_bridge_client()
    game_uuid = await client.game()
    response.headers["Location"] = request.url_for("game_details", game_uuid=game_uuid)
    return models.Game(uuid=game_uuid).dict(exclude_unset=True)


@router.get(
    "/{game_uuid}",
    name="game_details",
    summary="Get information about a game",
    response_model=models.Game,
)
async def get_game_details(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid)
):
    client = utils.get_bridge_client()
    deal = await client.get_deal(game=game_uuid, player=player_uuid)
    return models.Game(uuid=game_uuid, deal=deal)


@router.post(
    "/{game_uuid}/players",
    name="game_players_list",
    summary="Add a player to a game",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def post_game_players(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """
    This call causes the authenticated user to be added as a player to the game
    identified by ``game_uuid``.
    """
    client = utils.get_bridge_client()
    await client.join(game=game_uuid, player=player_uuid)
