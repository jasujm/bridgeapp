"""Bridge protocol glue code for the bridgeapp API"""

import zmq.asyncio

from bridgeapp import bridgeprotocol, settings

_ctx = zmq.asyncio.Context()


async def create_client():
    """Create new bridge client"""
    s = settings.get_settings()
    return await bridgeprotocol.BridgeClient.create(
        _ctx, s.backend_endpoint, curve_keys=s.curve_keys
    )
