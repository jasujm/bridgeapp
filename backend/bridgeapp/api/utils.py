"""
API utilities
.............
"""

import asyncio
import contextlib
import uuid

from bridgeapp import bridgeprotocol

from . import _bridgeprotocol


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
def subscribe_events(game_id: uuid.UUID):
    """Subscribe to events from a game

    The return value of this function can be used as a context manager that
    yields an event producer object. It exposes `get_event()` coroutine that can
    be used to get events about the game.

    .. code-block:: python

       with get_event_producer(uuid) as producer:
           while interested_in_events():
               consume(await producer.get_event())

    Parameters:
        game_id: The UUID of the game

    Returns:
        An event producer used to retrieve events about the given game
    """
    event_demultiplexer = _bridgeprotocol.get_event_demultiplexer()
    producer = event_demultiplexer.subscribe(game_id)
    try:
        yield producer
    finally:
        event_demultiplexer.unsubscribe(producer)


@contextlib.contextmanager
def autocancel_tasks():
    """Create asynchronous tasks that are guaranteed to be canceled

    This function returns a context manager that can be used to create
    tasks that are automatically canceled when the context manager
    exists. For example:

    .. code-block:: python

       with create_autocanceling_tasks() as create_task:
           task1 = create_task(coro1())
           task2 = create_task(coro2())
           await asyncio.gather(task1, task2)

    In the above example, even if ``task1`` would raise exception
    before ``task2`` completes, the context manager ensures that
    ``task2`` will be canceled.
    """
    tasks = []

    def _create_autocancelling_task(task):
        if asyncio.iscoroutine(task):
            task = asyncio.create_task(task)
        tasks.append(task)
        return task

    try:
        yield _create_autocancelling_task
    finally:
        for task in tasks:
            task.cancel()
