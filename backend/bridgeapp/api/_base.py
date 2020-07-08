"""Bridge API base definitions"""

import fastapi

from . import games

subapp = fastapi.FastAPI()

subapp.include_router(games.router, prefix="/games", tags=["games"])
