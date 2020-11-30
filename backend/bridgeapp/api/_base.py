"""Bridge API base definitions"""

import fastapi

from bridgeapp import bridgeprotocol

from . import models, games

subapp = fastapi.FastAPI()

subapp.include_router(games.router, prefix="/games", tags=["games"])


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
