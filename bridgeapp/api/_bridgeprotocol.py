"""Bridge protocol dependency for the bridgeapp API"""

import zmq.asyncio

from .. import bridgeprotocol

# This is rather weird stateful module but until I understand FastAPI
# better to refactor it, disable pylint nagging about it
# pylint: disable=invalid-name,global-statement

_ctx = zmq.asyncio.Context()
_bridge_client = None


async def startup():
    """Initialize client at startup"""
    global _bridge_client
    _bridge_client = await bridgeprotocol.BridgeClient.create(
        _ctx, "tcp://localhost:5555"
    )


def shutdown():
    """Close client at shutdown"""
    _bridge_client.close()


def get_client():
    """Get bridge client"""
    return _bridge_client
