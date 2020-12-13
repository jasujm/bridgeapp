"""Bridge client"""

import asyncio
import functools
import typing
import uuid

import orjson
import zmq.asyncio

from .. import models

from . import _base, utils, exceptions


OptionalUuid = typing.Optional[uuid.UUID]


_STATUS_EXCEPTION_MAP = {
    "UNK": exceptions.UnknownClientError("Unknown client"),
    "NF": exceptions.NotFoundError("Game not found"),
    "AE": exceptions.AlreadyExistsError("Game already exists"),
    "NA": exceptions.NotAuthorizedError("Not authorized"),
    "SR": exceptions.SeatReservedError("Seat already reserved"),
    "RV": exceptions.RuleViolationError("Rule violation"),
}


def _retries_handshake(func):
    @functools.wraps(func)
    async def wrapped(self, *args, **kwargs):
        while True:
            try:
                return await func(self, *args, **kwargs)
            except exceptions.UnknownClientError:
                await self.hello()

    return wrapped


class BridgeClient(_base.ClientBase):
    """Client for a bridge backend server"""

    @classmethod
    async def create(
        cls,
        ctx: zmq.asyncio.Context,
        endpoint: str,
        *,
        curve_keys: typing.Optional[_base.CurveKeys] = None,
    ) -> "BridgeClient":
        """Create client and perform handshake with the server

        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
            curve_keys: If given, the CURVE keys that will be used to establish
                the connection to the backend

        Returns:
            An initialized client that has performed the handshake
            with the server

        Raises:
            :exc:`exceptions.ProtocolError`: If performing the connection or the
                handshake fails
        """
        client = cls(ctx, endpoint, curve_keys=curve_keys)
        try:
            await client.hello()
            return client
        except:
            client.close()
            raise

    def __init__(
        self,
        ctx: zmq.asyncio.Context,
        endpoint: str,
        *,
        curve_keys: typing.Optional[_base.CurveKeys] = None,
    ):
        """
        Parameters:
            ctx: The ZeroMQ context
            endpoint: The server endpoint
            curvekeys: If given, the CURVE keys that will be used to establish
                       the connection to the backend
        """
        super().__init__(ctx, endpoint, curve_keys=curve_keys)
        self._handshake_pending = False
        self._handshake_lock = asyncio.Lock()

    async def hello(self):
        """Perform handshake with the server"""
        # Just one caller should perform the handshake at one time
        self._handshake_pending = True
        async with self._handshake_lock:
            if self._handshake_pending:
                await self.command("bridgehlo", version="0.1", role="client")
                self._handshake_pending = False

    @_retries_handshake
    async def game(
        self, *, game: OptionalUuid = None, args: typing.Optional[typing.Mapping] = None
    ) -> uuid.UUID:
        """Send game command to the server"""
        reply = await self.command("game", game=game, args=args)
        return self._convert_reply_safe(uuid.UUID, reply, "game", command="game")

    @_retries_handshake
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

    @_retries_handshake
    async def leave(
        self, *, game: uuid.UUID, player: uuid.UUID,
    ):
        """Send leave command to the server"""
        await self.command("leave", game=game, player=player)

    @_retries_handshake
    async def get(
        self, *, game: uuid.UUID, player: OptionalUuid = None, get: typing.List[str]
    ):
        """Send get command to the server"""
        reply = await self.command("get", game=game, player=player, get=get)
        return self._convert_reply_safe(lambda r: r, reply, "get", command="get")

    @_retries_handshake
    async def get_deal(
        self, *, game: uuid.UUID, player: OptionalUuid = None
    ) -> typing.Tuple[models.Deal, int]:
        """Get the deal state from the server

        Parameters:
            game: The UUID of the game
            player: The player requesting deal information

        Returns:
            A tuple containing the deal state, and the running counter, respectively
        """
        reply = await self.command(
            "get", game=game, player=player, get=["pubstate", "privstate"]
        )
        return (
            self._convert_reply_safe(self._create_deal, reply, "get", command="get"),
            self._convert_reply_safe(int, reply, "counter", command="get"),
        )

    @_retries_handshake
    async def get_self(self, *, game: uuid.UUID, player: OptionalUuid = None):
        """Get the player state from the server"""
        reply = await self.command("get", game=game, player=player, get=["self"])
        return self._convert_reply_safe(
            self._create_player_state, reply, "get", command="get"
        )

    @_retries_handshake
    async def get_results(self, *, game: uuid.UUID):
        """Get the deal results from the server"""
        reply = await self.command("get", game=game, get=["results"])
        return self._convert_reply_safe(
            self._create_deal_results, reply, "get", command="get"
        )

    @_retries_handshake
    async def get_players(self, *, game: uuid.UUID):
        """Get the players in a game from the server"""
        reply = await self.command("get", game=game, get=["players"])
        return self._convert_reply_safe(
            self._create_players_map, reply, "get", command="get"
        )

    @_retries_handshake
    async def call(
        self, *, game: uuid.UUID, player: OptionalUuid = None, call: models.Call
    ):
        """Send call command to the server"""
        await self.command("call", game=game, player=player, call=call)

    @_retries_handshake
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
    def _create_deal(get):
        pubstate = get["pubstate"]
        privstate = get["privstate"]
        if pubstate is None:
            return None
        assert isinstance(pubstate, dict)
        assert isinstance(privstate, dict)
        state = utils.merge_patch(pubstate, privstate)
        deal_uuid = state.pop("deal")
        return models.Deal(uuid=deal_uuid, **state)

    @staticmethod
    def _create_player_state(get):
        return models.PlayerState(**get["self"])

    @staticmethod
    def _create_deal_results(get):
        return [
            models.DealResult(
                deal=models.PartialDeal(uuid=result["deal"]), result=result["result"]
            )
            for result in get["results"]
        ]

    @staticmethod
    def _create_players_map(get):
        return models.PlayersInGame(
            **{
                position: uuid and models.Player(uuid=uuid)
                for (position, uuid) in get["players"].items()
            }
        )

    def _create_command_failure_exception(self, status: bytes):
        code = utils.get_error_code(status)
        if ex := _STATUS_EXCEPTION_MAP.get(code):
            return ex
        return super()._create_command_failure_exception(status)
