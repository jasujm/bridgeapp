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


class _EventProducer:
    def __init__(self, game_uuid: uuid.UUID):
        self._queue = asyncio.Queue()
        self._game_uuid = game_uuid

    def produce(self, event: bridgeprotocol.BridgeEvent):
        """Produce an event about the game"""
        self._queue.put_nowait(event)

    async def get_event(self) -> bridgeprotocol.BridgeEvent:
        """Get the next event about the game"""
        return await self._queue.get()

    @property
    def game_uuid(self):
        """The UUID of the game"""
        return self._game_uuid


class EventDemultiplexer:
    """Demultiplexer for game events"""

    def __init__(self, event_receiver: bridgeprotocol.BridgeEventReceiver):
        """
        Parameters:
            event_receiver: The underlying event receiver
        """
        self._event_receiver = event_receiver
        self._producers = defaultdict(list)

    def subscribe(self, game_uuid: uuid.UUID):
        """Subscribe to events about a game"""
        if not self._producers:
            loop = asyncio.get_running_loop()
            loop.create_task(self._produce_events())
        producer = _EventProducer(game_uuid)
        self._producers[game_uuid].append(producer)
        return producer

    def unsubscribe(self, producer: _EventProducer):
        """Unsubscribe from events about a game"""
        producers_for_game = self._producers[producer.game_uuid]
        producers_for_game.remove(producer)
        if not producers_for_game:
            del self._producers[producer.game_uuid]

    async def _produce_events(self):
        while self._producers:
            event = await self._event_receiver.get_event()
            if producers := self._producers.get(event.game):
                for producer in producers[:]:
                    producer.produce(event)
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
