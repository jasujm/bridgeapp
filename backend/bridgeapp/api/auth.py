"""
API authentication services
---------------------------
"""

import contextlib

import fastapi

from bridgeapp import db

from . import db_utils

_security = fastapi.security.HTTPBasic()


async def get_authenticated_player(
    credentials: fastapi.security.HTTPBasicCredentials = fastapi.Depends(_security),
):
    """Get the identity of the authenticated player

    This function is consumed as a dependency by a FastAPI router. It reads the
    credentials and returns the ID of the authenticated player. If verifying the
    credentials fails, a HTTP 401 status is raised.
    """
    player = None
    with contextlib.suppress(db_utils.NotFoundError):
        player = await db_utils.load(
            db.players, credentials.username, key=db.players.c.username
        )
    if not player or player.password != credentials.password:
        raise fastapi.HTTPException(status_code=fastapi.status.HTTP_401_UNAUTHORIZED)
    return player._mapping
