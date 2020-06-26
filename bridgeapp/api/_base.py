"""Bridge API base definitions"""

import fastapi

from . import _bridgeprotocol, games

router = fastapi.APIRouter()

router.include_router(games.router, prefix="/games", tags=["games"])


@router.on_event("startup")
async def _startup_event():
    await _bridgeprotocol.startup()


@router.on_event("shutdown")
def _shutdown_event():
    _bridgeprotocol.shutdown()
