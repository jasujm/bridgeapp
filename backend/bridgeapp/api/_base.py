"""Bridge API base definitions"""

import fastapi

from bridgeapp import bridgeprotocol

from . import models, games, deals, players

subapp = fastapi.FastAPI(
    title="Contract bridge API",
    description="""API for playing contract bridge. Work in progress.""",
    version="0.1",
)

subapp.include_router(games.router, prefix="/games", tags=["games"])
subapp.include_router(deals.router, prefix="/deals", tags=["deals"])
subapp.include_router(players.router, prefix="/players", tags=["players"])


@subapp.middleware("http")
async def add_counter_middleware(request: fastapi.Request, call_next):
    """Add X-Counter header to the response if set"""
    request.state.counter_header_value = None
    response = await call_next(request)
    if (counter := request.state.counter_header_value) is not None:
        response.headers[games.COUNTER_HEADER] = str(counter)
    return response


def _exception_response(status: int, ex: Exception):
    error = models.Error(detail=str(ex))
    return fastapi.responses.JSONResponse(status_code=status, content=error.dict())


@subapp.exception_handler(bridgeprotocol.NotFoundError)
def handle_not_found(request, ex):
    """Convert :exc:`bridgeprotocol.NotFounderror` into HTTP error"""
    del request
    return _exception_response(fastapi.status.HTTP_404_NOT_FOUND, ex)


@subapp.exception_handler(bridgeprotocol.SeatReservedError)
def handle_seat_reserved(request, ex):
    """Convert :exc:`bridgeprotocol.SeatReservederror` into HTTP error"""
    del request
    return _exception_response(fastapi.status.HTTP_409_CONFLICT, ex)


@subapp.exception_handler(bridgeprotocol.RuleViolationError)
def handle_rule_violation(request, ex):
    """Convert :exc:`bridgeprotocol.RuleViolationError` into HTTP error"""
    del request
    return _exception_response(fastapi.status.HTTP_409_CONFLICT, ex)
