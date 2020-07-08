"""Bridge API base definitions"""

import fastapi

from . import games

router = fastapi.APIRouter()

router.include_router(games.router, prefix="/games", tags=["games"])
