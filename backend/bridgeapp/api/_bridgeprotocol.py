"""Bridge protocol glue code for the bridgeapp API"""

import zmq.asyncio

from bridgeapp import bridgeprotocol
from bridgeapp.settings import settings

_ctx = zmq.asyncio.Context()


async def create_client():
    """Create new bridge client"""
    return await bridgeprotocol.BridgeClient.create(
        _ctx, settings.backend_endpoint, curve_keys=settings.curve_keys
    )
