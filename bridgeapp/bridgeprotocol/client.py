"""Bridge client"""

import enum
import json
import typing
import uuid

import pydantic
import zmq.asyncio

from .. import models

from . import _base, utils


class _BridgeEncoder(json.JSONEncoder):
    """JSON encoder that handles types in the bridge protocol"""

    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o)
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, pydantic.BaseModel):
            return o.dict()
        return json.JSONEncoder.default(self, o)


class BridgeClient(_base.ClientBase):
    """Client for a bridge backend server"""

    _encoder = _BridgeEncoder()
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

        Raises:
            :exc:`exceptions.ProtocolError`: If performing the connection or the
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
