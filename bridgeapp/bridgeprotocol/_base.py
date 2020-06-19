"""Low-level base classes"""

import abc
import asyncio
import contextlib
import logging
import sys
import typing

import zmq
import zmq.asyncio

from . import exceptions, utils

logger = logging.getLogger(__name__)


RawArgumentsInput = typing.Mapping[bytes, bytes]
RawArgumentsOutput = typing.Dict[bytes, bytes]


class SocketBase(contextlib.AbstractContextManager, abc.ABC):
    """Base class

    This class implements common functionality for client
    implementations wrapping a ZeroMQ socket and dealing with
    serialization and deserialization of messages.
    """

    def __init__(self, socket: zmq.Socket, endpoint: str):
        """
        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
        """
        self._socket = socket
        self._socket.connect(endpoint)

    def close(self):
        """Close the underlying sockets"""
        self._socket.close()

    def __exit__(self, *exc_args):
        self.close()

    @abc.abstractmethod
    def _deserialize(self, arg: bytes):
        """Deserialize ``arg``"""

    def _deserialize_all(self, args):
        return {k.decode(): self._deserialize(v) for (k, v) in args.items()}


class ClientBase(SocketBase):
    """Base for bridge protocol client"""

    def __init__(self, ctx: zmq.asyncio.Context, endpoint: str):
        """
        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
        """
        super().__init__(ctx.socket(zmq.DEALER), endpoint)  # pylint: disable=no-member
        self._counter = 0
        self._replies_pending = {}

    async def command(self, command: str, **kwargs) -> typing.Dict[str, typing.Any]:
        """Send a command to the server

        This method sends the command identified by ``command`` with
        command arguments from ``kwargs`` to the server.

        Parameters:
            command: The command
            kwargs: The command arguments as key-value pairs

        Returns:
            A dictionary containing the reply arguments

        Raises:
            :exc:`exceptions.ProtocolError`: To signal errors in the exchange
        """
        raw_command = command.encode()
        raw_command_arguments = self._serialize_all(kwargs)
        raw_reply_arguments = await self._raw_command(
            raw_command, raw_command_arguments
        )
        return self._deserialize_all(raw_reply_arguments)

    async def _raw_command(
        self, identifier: bytes, command_arguments: RawArgumentsInput
    ) -> RawArgumentsOutput:
        """Send a raw command to the server

        This is a low-level method similar to :meth:`command()` except
        that instead of dealing with Python objects it deals with
        objects that are already in wire format.

        Parameters:
            identifier: The command identifier frame
            command_arguments: The command arguments

        Returns:
            A tuple containing the status and reply arguments, respectively
        """
        tag = self._counter.to_bytes(2, byteorder=sys.byteorder)
        self._counter = (self._counter + 1) % 65536
        msg = [b"", tag, identifier, *utils.flatten_arguments(command_arguments)]
        logger.debug("Sending message: %r", msg)
        await self._socket.send_multipart(msg)
        # Instead of awaiting the reply directly, do it indirectly by
        # awaiting a future yielding the reply. The pending replies
        # may be fulfilled in any order in _receive_replies(), so out
        # of order replies are handled correctly.
        loop = asyncio.get_running_loop()
        reply_future = loop.create_future()
        create_receive_task = not self._replies_pending
        self._replies_pending[tag] = reply_future
        if create_receive_task:
            loop.create_task(self._receive_replies())
        return await reply_future

    @abc.abstractmethod
    def _serialize(self, arg) -> bytes:
        """Serialize ``arg``"""

    def _serialize_all(self, args):
        return {
            k.encode(): self._serialize(v) for (k, v) in args.items() if v is not None
        }

    async def _receive_replies(self):
        while self._replies_pending:
            frames = await self._socket.recv_multipart()
            logger.debug("Received reply: %r", frames)
            if len(frames) < 2:
                logger.warning("Discarding reply: %r", frames)
                continue
            tag = frames[1]
            if reply_future := self._replies_pending.pop(tag, None):
                if len(frames) < 3:
                    reply_future.set_exception(
                        exceptions.InvalidMessage(
                            "Missing status frame in reply: {frames!r}"
                        )
                    )
                    continue
                status, *reply_arguments = frames[2:]
                if len(reply_arguments) % 2 != 0:
                    reply_future.set_exception(
                        exceptions.InvalidMessage(
                            f"Odd number of argument frames in reply: {frames!r}"
                        )
                    )
                elif not utils.is_status_successful(status):
                    reply_future.set_exception(
                        exceptions.CommandFailure("Command returned with failure")
                    )
                else:
                    reply_future.set_result(utils.group_arguments(reply_arguments))
            else:
                logger.warning("Discarding reply containing unknown tag: %r", frames)

    @staticmethod
    def _convert_reply_safe(factory, reply, key, *, command="<unknown>"):
        """Convert reply to an expected format

        Calls ``factory(reply[key])``, converting any error to
        :exc:`exceptions.InvalidMessage`. This is intended to be used
        to convert the reply of an received command to a format
        expected by the client.
        """
        try:
            return factory(reply[key])
        except exceptions.ProtocolError:
            raise
        except Exception:
            raise exceptions.InvalidMessage(f"Unexpected reply to {command}: {reply!r}")


class EventReceiverBase(SocketBase):
    """Base for bridge protocol event receiver"""

    def __init__(self, ctx: zmq.asyncio.Context, endpoint: str):
        """
        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
        """
        # pylint: disable=no-member
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, b"")
        super().__init__(socket, endpoint)

    async def events(self):
        """Receive events from the server

        Instead of raising an exception like :meth:`get_event()`, the
        generator returned by this method simply drops invalid
        messages with warning.

        Returns:
            An asynchronous generator that yields events received from
            the server
        """
        while not self._socket.closed:
            try:
                yield await self.get_event()
            except Exception:  # pylint: disable=broad-except
                logger.warning("Discarding event", exc_info=True)

    async def get_event(self):
        """Receive an event from the server

        Returns:
            A tuple containing the events received from the
            server
        """
        raw_tag, raw_event_arguments = await self._get_raw_event()
        tag = raw_tag.decode()
        event_arguments = self._deserialize_all(raw_event_arguments)
        return self._create_event(tag, **event_arguments)

    async def _get_raw_event(self) -> typing.Tuple[bytes, RawArgumentsOutput]:
        """Receive an event from the server

        This is a low-level method similar to :meth:`get_event()`
        except that instead of dealing with Python objects it deals
        with objects that are already in wire format.

        Returns:
            A tuple containing the event frame and event arguments,
            respectively

        Raises:
            :exc:`exceptions.InvalidMessage`: If the event message is invalid
        """
        tag, *event_arguments = await self._socket.recv_multipart()
        logger.debug("Received event: %r, %r", tag, event_arguments)
        if len(event_arguments) % 2 != 0:
            raise exceptions.InvalidMessage(
                f"Odd number of argument frames in event {tag!r}: {event_arguments!r}"
            )
        return tag, utils.group_arguments(event_arguments)

    @abc.abstractmethod
    def _create_event(self, tag: str, **kwargs):
        """Create event from event data

        Parameters:
            tag: The event tag
            kwargs: The event arguments as key-value pairs
        """
