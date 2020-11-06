"""Bridge protocol glue code for the bridgeapp API"""

import asyncio
from collections import defaultdict
import threading
import uuid

import zmq.asyncio

from bridgeapp import bridgeprotocol
from bridgeapp.settings import settings

_ctx = zmq.asyncio.Context()
_threadlocal = threading.local()


class EventDemultiplexer:  # pylint: disable=too-few-public-methods
    """Demultiplexer for game events"""

    def __init__(self, event_receiver: bridgeprotocol.BridgeEventReceiver):
        """
        Parameters:
            event_receiver: The underlying event receiver
        """
        self._event_receiver = event_receiver
        self._events_pending = defaultdict(list)

    async def get_event(self, game_uuid: uuid.UUID) -> bridgeprotocol.BridgeEvent:
        """Get the next event for a given game

        Parameters:
            game_uuid: The UUID of the game

        Returns:
            The next event from the underlying event received belonging to the
            given game
        """
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        create_receive_task = not self._events_pending
        self._events_pending[game_uuid].append(future)
        if create_receive_task:
            loop.create_task(self._receive_events())
        return await future

    async def _receive_events(self):
        while self._events_pending:
            event = await self._event_receiver.get_event()
            if futures := self._events_pending.get(event.game):
                for future in futures:
                    if not future.cancelled():
                        future.set_result(event)
                del self._events_pending[event.game]
                # Yield to give the receivers chance to renew their subscription
                await asyncio.sleep(0)


async def get_bridge_client() -> bridgeprotocol.BridgeClient:
    """Create thread local BridgeClient object"""
    if client := getattr(_threadlocal, "client", None):
        return client
    client = await bridgeprotocol.BridgeClient.create(
        _ctx, settings.backend_endpoint, curve_keys=settings.curve_keys
    )
    _threadlocal.client = client
    return client


def get_event_demultiplexer() -> EventDemultiplexer:
    """Create thread local EventDemultiplexer object"""
    if demultiplexer := getattr(_threadlocal, "demultiplexer", None):
        return demultiplexer
    demultiplexer = EventDemultiplexer(_create_event_receiver())
    _threadlocal.demultiplexer = demultiplexer
    return demultiplexer


def _create_event_receiver():
    return bridgeprotocol.BridgeEventReceiver(
        _ctx, settings.backend_event_endpoint, curve_keys=settings.curve_keys
    )
