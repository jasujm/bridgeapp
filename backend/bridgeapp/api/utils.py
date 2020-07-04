"""
Bridgeapp API utilities
-----------------------
"""

import threading
import uuid

from bridgeapp import bridgeprotocol
from bridgeapp.settings import settings

from . import _bridgeprotocol


PLAYER_UUID_NS = uuid.uuid5(settings.uuid_namespace, "players")
"""UUID namespace for bridge players"""


def generate_player_uuid(username: str) -> uuid.UUID:
    """Generate UUID for a player from ``username``"""
    return uuid.uuid5(PLAYER_UUID_NS, username)


async def get_bridge_client() -> bridgeprotocol.BridgeClient:
    """Get a bridge client

    This function returns, possibly after creating, a bridge client
    that is used to communicate with the bridge backend. It is
    settings aware.

    ZeroMQ sockets are not thread safe. That is why a separate client
    object is created and returned for each thread calling this
    function.
    """
    threadlocal = threading.local()
    if client := getattr(threadlocal, "bridge_client", None):
        return client
    client = await _bridgeprotocol.create_client()
    threadlocal.bridge_client = client
    return client
