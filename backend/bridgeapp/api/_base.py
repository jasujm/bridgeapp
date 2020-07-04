"""Bridge API base definitions"""

import fastapi

from . import _bridgeprotocol, games

router = fastapi.APIRouter()

router.include_router(games.router, prefix="/games", tags=["games"])
