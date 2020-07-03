"""
Bridge API games endpoints
--------------------------
"""

import uuid

import fastapi

from bridgeapp import bridgeprotocol, models as base_models

from . import models, utils

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
    This call causes a new game to be created. The server SHALL generate an UUID
    for the game and return it in the response body.
    """
    client = utils.get_bridge_client()
    try:
        game_uuid = await client.game()
    except bridgeprotocol.CommandFailure:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Error"
        )
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
    """
    The response contains a representation of the game from the point of
    view of the authenticated player. If the player is not in the game, only
    public information will be retrieved.
    """
    client = utils.get_bridge_client()
    try:
        deal = await client.get_deal(game=game_uuid, player=player_uuid)
    except bridgeprotocol.CommandFailure:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Error"
        )
    return models.Game(uuid=game_uuid, deal=deal)


@router.get(
    "/{game_uuid}/self",
    name="game_self",
    summary="Get information about the authenticated player",
    response_model=base_models.PlayerState,
)
async def get_game_self(
    game_uuid: uuid.UUID, player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid)
):
    """
    The response contains information about the authenticated player itself
    within the game, including position and available moves.
    """
    client = utils.get_bridge_client()
    try:
        return await client.get_self(game=game_uuid, player=player_uuid)
    except bridgeprotocol.CommandFailure:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Error"
        )


@router.post(
    "/{game_uuid}/players",
    name="game_players",
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
    try:
        await client.join(game=game_uuid, player=player_uuid)
    except bridgeprotocol.CommandFailure:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Error"
        )


@router.post(
    "/{game_uuid}/calls",
    name="game_calls",
    summary="Add a call to the current bidding",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def post_game_calls(
    game_uuid: uuid.UUID,
    call: base_models.Call,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """
    This call causes the authenticated user to make a call (no pun intended) in
    specified in the body of the request. The call is only possible during the
    bidding phase of a deal, abiding to the laws of contract bridge.
    """
    client = utils.get_bridge_client()
    try:
        await client.call(game=game_uuid, player=player_uuid, call=call)
    except bridgeprotocol.CommandFailure:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Error"
        )


@router.post(
    "/{game_uuid}/trick",
    name="game_trick",
    summary="Add a card to the current trick",
    status_code=fastapi.status.HTTP_204_NO_CONTENT,
)
async def post_game_trick(
    game_uuid: uuid.UUID,
    card: base_models.CardType,
    player_uuid: uuid.UUID = fastapi.Depends(_get_player_uuid),
):
    """
    This call causes the authenticated user to play the card to the current
    specified in the body of the request. The call is only possible during the
    playing phase of a deal, abiding to the laws of contract bridge.
    """
    client = utils.get_bridge_client()
    try:
        await client.play(game=game_uuid, player=player_uuid, card=card)
    except bridgeprotocol.CommandFailure:
        raise fastapi.HTTPException(
            status_code=fastapi.status.HTTP_400_BAD_REQUEST, detail="Error"
        )
