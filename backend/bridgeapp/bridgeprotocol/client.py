"""Bridge client"""

import asyncio
import functools
import typing
import uuid

import orjson
import zmq.asyncio

from . import _base, models, utils, exceptions


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
    ) -> typing.Tuple[uuid.UUID, models.Position]:
        """Send join command to the server"""
        reply = await self.command("join", game=game, player=player, position=position)
        return (
            self._convert_reply_safe(uuid.UUID, reply, "game", command="join"),
            self._convert_reply_safe(
                models.Position, reply, "position", command="join"
            ),
        )

    @_retries_handshake
    async def leave(self, *, game: uuid.UUID, player: uuid.UUID) -> models.Position:
        """Send leave command to the server"""
        reply = await self.command("leave", game=game, player=player)
        return self._convert_reply_safe(
            lambda p: p and models.Position(p), reply, "position", command="leave"
        )

    @_retries_handshake
    async def get_game(
        self, *, game: uuid.UUID, player: OptionalUuid = None
    ) -> typing.Tuple[models.Game, int]:
        """Get the full state of a game from the server

        Parameters:
            game: The UUID of the game
            player: The player requesting deal information

        Returns:
            A tuple containing the game state, and the running counter, respectively
        """
        reply = await self.command(
            "get",
            game=game,
            player=player,
            get=["pubstate", "privstate", "self", "results", "players"],
        )
        return (
            self._convert_reply_safe(
                self._create_game(game), reply, "get", command="get"
            ),
            self._convert_reply_safe(int, reply, "counter", command="get"),
        )

    @_retries_handshake
    async def get_game_deal(
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
    async def get_deal(self, *, deal: uuid.UUID) -> models.Deal:
        """Get the deal record from the server

        Parameters:
            deal: The UUID of the game

        Returns:
            A deal record
        """
        reply = await self.command("get", deal=deal)
        return self._convert_reply_safe(self._create_deal, reply, "get", command="get")

    @_retries_handshake
    async def get_self(
        self, *, game: uuid.UUID, player: OptionalUuid = None
    ) -> typing.Tuple[models.PlayerState, int]:
        """Get the player state from the server

        Parameters:
            game: The UUID of the game
            player: The player requesting deal information

        Returns:
            A tuple containing the self state, and the running counter, respectively
        """
        reply = await self.command("get", game=game, player=player, get=["self"])
        return (
            self._convert_reply_safe(
                self._create_player_state, reply, "get", command="get"
            ),
            self._convert_reply_safe(int, reply, "counter", command="get"),
        )

    @_retries_handshake
    async def get_results(
        self, *, game: uuid.UUID
    ) -> typing.Tuple[typing.List[models.DealResult], int]:
        """Get the deal results from the server

        Parameters:
            game: The UUID of the game
            player: The player requesting deal information

        Returns:
            A tuple containing the results, and the running counter, respectively
        """
        reply = await self.command("get", game=game, get=["results"])
        return (
            self._convert_reply_safe(
                self._create_deal_results, reply, "get", command="get"
            ),
            self._convert_reply_safe(int, reply, "counter", command="get"),
        )

    @_retries_handshake
    async def get_players(
        self, *, game: uuid.UUID
    ) -> typing.Tuple[models.PlayersInGame, int]:
        """Get the players in a game from the server

        Parameters:
            game: The UUID of the game

        Returns:
            A tuple containing the players in the game, and the running counter,
            respectively
        """
        reply = await self.command("get", game=game, get=["players"])
        return (
            self._convert_reply_safe(
                self._create_players_map, reply, "get", command="get"
            ),
            self._convert_reply_safe(int, reply, "counter", command="get"),
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

    def _serialize(self, obj):
        return orjson.dumps(obj, default=dict)

    def _deserialize(self, obj):
        return orjson.loads(obj)

    @classmethod
    def _create_game(cls, game_id: uuid.UUID):
        def _create_game_inner(get):
            return models.Game(
                id=game_id,
                deal=cls._create_deal(get),
                self=cls._create_player_state(get),
                results=cls._create_deal_results(get),
                players=cls._create_players_map(get),
            )

        return _create_game_inner

    @staticmethod
    def _create_deal(get):
        pubstate = get["pubstate"]
        privstate = get.get("privstate", {})
        if pubstate is None:
            return None
        assert isinstance(pubstate, dict)
        assert isinstance(privstate, dict)
        state = utils.merge_patch(pubstate, privstate)
        deal_id = state.pop("deal")
        return models.Deal(id=deal_id, **state)

    @staticmethod
    def _create_player_state(get):
        return models.PlayerState(**get["self"])

    @staticmethod
    def _create_deal_results(get):
        return [models.DealResult(**result) for result in get["results"]]

    @staticmethod
    def _create_players_map(get):
        return models.PlayersInGame(**get["players"])

    def _create_command_failure_exception(self, status: bytes):
        code = utils.get_error_code(status)
        if ex := _STATUS_EXCEPTION_MAP.get(code):
            return ex
        return super()._create_command_failure_exception(status)
