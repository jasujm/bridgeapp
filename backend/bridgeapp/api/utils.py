"""
API utilities
.............
"""

import contextlib
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


@contextlib.contextmanager
def subscribe_events(game_uuid: uuid.UUID):
    """Subscribe to events from a game

    The return value of this function can be used as a context manager that
    yields an event producer object. It exposes `get_event()` coroutine that can
    be used to get events about the game.

    .. code-block:: python

       with get_event_producer(uuid) as producer:
           while interested_in_events():
               consume(await producer.get_event())

    Parameters:
        game_uuid: The UUID of the game

    Returns:
        An event producer used to retrieve events about the given game
    """
    event_demultiplexer = _bridgeprotocol.get_event_demultiplexer()
    producer = event_demultiplexer.subscribe(game_uuid)
    try:
        yield producer
    finally:
        event_demultiplexer.unsubscribe(producer)
