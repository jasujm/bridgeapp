"""Bridge client"""

import typing
import uuid

import orjson
import zmq.asyncio

from .. import models

from . import _base, utils


OptionalUuid = typing.Optional[uuid.UUID]


class BridgeClient(_base.ClientBase):
    """Client for a bridge backend server"""

    @classmethod
    async def create(
        cls, ctx: zmq.asyncio.Context, endpoint: str, *, identity: bytes = None
    ) -> "BridgeClient":
        """Create client and perform handshake with the server

        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
            identity: The socket identity

        Returns:
            An initialized client that has performed the handshake
            with the server

        Raises:
            :exc:`exceptions.ProtocolError`: If performing the connection or the
                handshake fails
        """
        client = cls(ctx, endpoint, identity=identity)
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
        self, *, game: OptionalUuid = None, args: typing.Optional[typing.Mapping] = None
    ) -> uuid.UUID:
        """Send game command to the server"""
        reply = await self.command("game", game=game, args=args)
        return self._convert_reply_safe(uuid.UUID, reply, "game", command="game")

    async def join(
        self,
        *,
        game: OptionalUuid = None,
        player: OptionalUuid = None,
        position: typing.Optional[models.Position] = None,
    ) -> uuid.UUID:
        """Send join command to the server"""
        reply = await self.command("join", game=game, player=player, position=position)
        return self._convert_reply_safe(uuid.UUID, reply, "game", command="join")

    async def get(
        self, *, game: uuid.UUID, player: OptionalUuid = None, get: typing.List[str]
    ):
        """Send get command to the server"""
        reply = await self.command("get", game=game, player=player, get=get)
        return self._convert_reply_safe(lambda r: r, reply, "get", command="get")

    async def get_deal(self, *, game: uuid.UUID, player: OptionalUuid = None):
        """Get the deal state from the server"""
        reply = await self.command(
            "get", game=game, player=player, get=["pubstate", "privstate"]
        )
        return self._convert_reply_safe(
            self._create_deal_state, reply, "get", command="get"
        )

    async def get_self(self, *, game: uuid.UUID, player: OptionalUuid = None):
        """Get the player state from the server"""
        reply = await self.command("get", game=game, player=player, get=["self"])
        return self._convert_reply_safe(
            self._create_player_state, reply, "get", command="get"
        )

    async def call(
        self, *, game: uuid.UUID, player: OptionalUuid = None, call: models.Call
    ):
        """Send call command to the server"""
        await self.command("call", game=game, player=player, call=call)

    async def play(
        self, *, game: uuid.UUID, player: OptionalUuid = None, card: models.CardType
    ):
        """Send play command to the server"""
        await self.command("play", game=game, player=player, card=card)

    @classmethod
    def _serialize(cls, obj):
        return orjson.dumps(obj, default=dict)

    @staticmethod
    def _deserialize(obj):
        return orjson.loads(obj)

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
