"""Bridge protocol glue code for the bridgeapp API"""

import zmq.asyncio

from bridgeapp import bridgeprotocol, settings

# This is rather weird stateful module but until I understand FastAPI
# better to refactor it, disable pylint nagging about it
# pylint: disable=invalid-name,global-statement

_ctx = zmq.asyncio.Context()
_bridge_client = None


async def startup():
    """Initialize client at startup"""
    global _bridge_client
    s = settings.get_settings()
    _bridge_client = await bridgeprotocol.BridgeClient.create(
        _ctx, s.backend_endpoint, curve_keys=s.curve_keys
    )


def shutdown():
    """Close client at shutdown"""
    _bridge_client.close()
