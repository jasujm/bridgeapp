"""
Bridge protocol implementation
------------------------------

The :mod:`bridgeprotocol` module contains classes and utilities for
communicating with the bridge backend server.
"""

import abc
import asyncio
import contextlib
import enum
import json
import logging
import sys
import typing
import uuid

import more_itertools as mi
import pydantic
import zmq
import zmq.asyncio

from . import models, utils

logger = logging.getLogger(__name__)

RawArgumentsInput = typing.Mapping[bytes, bytes]
RawArgumentsOutput = typing.Dict[bytes, bytes]

ArgumentsInput = typing.Mapping[str, typing.Any]
ArgumentsOutput = typing.Dict[str, typing.Any]


class ProtocolError(Exception):
    """Generic protocol error"""


class InvalidMessage(ProtocolError):
    """Error signaling invalid message received from the server"""


class CommandFailure(ProtocolError):
    """Error signaling failed command"""


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
        """Send a structured command to the server

        This method sends the command identified by ``command`` with
        command arguments from ``kwargs`` to the server. To convert
        between Python and wire formats, it relies on :meth:`encode()`
        and :meth:`_deserialize()` being implemented by the derived
        class.

        Parameters:
            command: The command
            kwargs: The command arguments as key-value pairs. The
                    arguments will be serialized with
                    :meth:`serialize()`.

        Returns:
            A dictionary containing the reply arguments. The reply
            arguments will be deserialized with :meth:`_deserialize()`.

        Raises:
            :exc:`ProtocolError` or one of its subclasses to signal
            errors in the exchange

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
        """Send a command to the server

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
        msg = [b"", tag, identifier, *_flatten_arguments(command_arguments)]
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
                        InvalidMessage("Missing status frame in reply: {frames!r}")
                    )
                    continue
                status, *reply_arguments = frames[2:]
                if len(reply_arguments) % 2 != 0:
                    reply_future.set_exception(
                        InvalidMessage(
                            f"Odd number of argument frames in reply: {frames!r}"
                        )
                    )
                elif not _is_status_successful(status):
                    reply_future.set_exception(
                        CommandFailure("Command returned with failure")
                    )
                else:
                    reply_future.set_result(_group_arguments(reply_arguments))
            else:
                logger.warning("Discarding reply containing unknown tag: %r", frames)

    @staticmethod
    def _convert_reply_safe(factory, reply, key, *, command="<unknown>"):
        """Convert reply to an expected format

        Calls ``factory(reply[key])``, converting any error to
        :exc:`InvalidMessage`. This is intended to be used to convert
        the reply of an received command to a format expected by the
        client.
        """
        try:
            return factory(reply[key])
        except ProtocolError:
            raise
        except Exception:
            raise InvalidMessage(f"Unexpected reply to {command}: {reply!r}")


class BridgeEncoder(json.JSONEncoder):
    """JSON encoder that handles types in the bridge protocol"""

    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, pydantic.BaseModel):
            return o.dict()
        return json.JSONEncoder.default(self, o)


class BridgeClient(ClientBase):
    """Client for a bridge backend server"""

    _encoder = BridgeEncoder()
    GameUuid = typing.Optional[uuid.UUID]
    PlayerUuid = typing.Optional[uuid.UUID]

    @classmethod
    async def create(cls, ctx: zmq.asyncio.Context, endpoint: str) -> "BridgeClient":
        """Create client and perform handshake with the server

        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint

        Returns:
            An initialized client that has performed the handshake
            with the server

        Raise:
            :exc:`ProtocolError` if performing the connection or the
            handshake fails
        """
        client = cls(ctx, endpoint)
        try:
            await client.hello()
            return client
        except:
            client.close()
            raise

    async def hello(self):
        """Perform handshake with the server"""
        await self.command("bridgehlo", version="0.1", role="client")

    async def game(
        self, *, game: GameUuid = None, args: typing.Optional[typing.Mapping] = None
    ) -> uuid.UUID:
        """Send game command to the server"""
        reply = await self.command("game", game=game, args=args)
        return self._convert_reply_safe(uuid.UUID, reply, "game", command="game")

    async def join(
        self,
        *,
        game: GameUuid = None,
        player: PlayerUuid = None,
        position: typing.Optional[models.Position] = None,
    ) -> uuid.UUID:
        """Send join command to the server"""
        reply = await self.command("join", game=game, player=player, position=position)
        return self._convert_reply_safe(uuid.UUID, reply, "game", command="join")

    async def get_deal(self, *, game: GameUuid = None, player: PlayerUuid = None):
        """Get the deal state from the server"""
        reply = await self.command(
            "get", game=game, player=player, get=["pubstate", "privstate"]
        )
        return self._convert_reply_safe(
            self._create_deal_state, reply, "get", command="get"
        )

    async def get_player(self, *, game: GameUuid = None, player: PlayerUuid = None):
        """Get the player state from the server"""
        reply = await self.command("get", game=game, player=player, get=["self"])
        return self._convert_reply_safe(
            self._create_player_state, reply, "get", command="get"
        )

    async def call(
        self, *, game: GameUuid = None, player: PlayerUuid = None, call: models.Call
    ):
        """Send call command to the server"""
        await self.command("call", game=game, player=player, call=call)

    async def play(
        self, *, game: GameUuid = None, player: PlayerUuid = None, card: models.CardType
    ):
        """Send play command to the server"""
        await self.command("play", game=game, player=player, card=card)

    @classmethod
    def _serialize(cls, arg):
        return cls._encoder.encode(arg).encode()

    @staticmethod
    def _deserialize(arg):
        return json.loads(arg)

    @staticmethod
    def _create_deal_state(get):
        pubstate = get["pubstate"]
        privstate = get["privstate"]
        assert isinstance(pubstate, dict)
        assert isinstance(privstate, dict)
        state = utils.merge_patch(pubstate, privstate)
        return models.DealState(**state)

    @staticmethod
    def _create_player_state(get):
        return models.PlayerState(**get["self"])


class EventReceiverBase(SocketBase):
    """Base for bridge protocol event receiver"""

    def __init__(self, ctx: zmq.asyncio.Context, endpoint: str):
        """
        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
        """
        socket = ctx.socket(zmq.SUB)
        socket.setsockopt(zmq.SUBSCRIBE, b"")
        super().__init__(socket, endpoint)  # pylint: disable=no-member

    async def events(self):
        """Receive structured events from the server

        Instead of raising an exception like :meth:`_get_event()`, the
        generator returned by this method simply drops invalid
        messages with warning.

        Returns:
            An asynchronous generator that yields tuples containing
            the events received from the server. The raw event
            arguments are first deserialized using
            :meth:`_deserialize()` and then constructed using
            :meth:`_create_event()`.
        """
        while not self._socket.closed:
            try:
                yield await self.get_event()
            except Exception:
                logger.warning("Discarding event", exc_info=True)

    async def get_event(self):
        """Receive an event from the server

        Returns:
            A tuple containing the events received from the
            server. The raw event arguments are first deserialized
            using :meth:`_deserialize()` and then constructed using
            :meth:`_create_event()`.
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
            :exc:`InvalidMessage` if the event message is invalid
        """
        tag, *event_arguments = await self._socket.recv_multipart()
        logger.debug("Received event: %r, %r", tag, event_arguments)
        if len(event_arguments) % 2 == 0:
            return tag, _group_arguments(event_arguments)
        else:
            raise InvalidMessage(
                f"Odd number of argument frames in event {tag!r}: {event_arguments!r}"
            )

    @abc.abstractmethod
    def _create_event(self, tag: str, **kwargs):
        """Create event from event data

        Parameters:
            tag: The event tag
            kwargs: The event arguments as key-value pairs
        """


class BridgeEvent(pydantic.BaseModel):
    """Bridge event"""

    game: uuid.UUID
    type: str

    class Config:  # pylint: disable=all
        extra = "allow"


class BridgeEventReceiver(EventReceiverBase):
    """Client for receiving events from a bridge backend server"""

    @staticmethod
    def _deserialize(arg):
        return json.loads(arg)

    @staticmethod
    def _create_event(tag: str, **kwargs) -> BridgeEvent:
        game, type = tag.split(":")
        return BridgeEvent(game=uuid.UUID(game), type=type, **kwargs)


def _group_arguments(args):
    return dict(mi.grouper(args, 2))


def _flatten_arguments(args):
    return mi.flatten(args.items())


def _is_status_successful(status):
    return status.startswith(b"OK")
