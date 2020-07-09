"""
Bridgeapp API utilities
-----------------------
"""

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
    return await _bridgeprotocol.get_bridge_client()


async def get_event(game_uuid: uuid.UUID) -> bridgeprotocol.BridgeEvent:
    """Get the next event for a given game

    This function returns the next event published by the bridge
    backend that belongs to the game identified by the argument.

    Parameters:
        game_uuid: The UUID of the game
    """
    event_demultiplexer = _bridgeprotocol.get_event_demultiplexer()
    return await event_demultiplexer.get_event(game_uuid)
