"""
Tests for the :mod:`bridgeapp.bridgeprotocol` module
"""

import asyncio
import copy
import itertools
import random
import uuid

import pytest
import zmq

from bridgeapp import bridgeprotocol
from bridgeapp.bridgeprotocol import models

from . import mocks


@pytest.fixture
def zmq_ctx():
    """Yield ZeroMQ context"""
    ctx = zmq.asyncio.Context()
    yield ctx
    ctx.term()


@pytest.fixture
def server(zmq_ctx, tmpdir):
    """Yield a :class:`mocks.MockBridgeServer` instance"""
    with mocks.MockBridgeServer(zmq_ctx, tmpdir) as srv:
        yield srv


@pytest.fixture
def client(zmq_ctx, server):
    """Yield a :class:`bridgeapp.bridgeprotocol.ClientBase` instance"""
    with bridgeprotocol.BridgeClient(zmq_ctx, server.endpoint) as clt:
        yield clt


@pytest.fixture
def event_receiver(zmq_ctx, server):
    """Yield a :class:`bridgeapp.bridgeprotocol.BridgeEventReceiver` instance"""
    with bridgeprotocol.BridgeEventReceiver(zmq_ctx, server.event_endpoint) as evr:
        yield evr


@pytest.fixture
async def event_generator(event_receiver):
    """Yield a raw event generator and cleanup afterwards"""
    async for gen in _event_generator_helper(event_receiver, event_receiver.events):
        yield gen


@pytest.fixture(
    params=list(
        itertools.product([b"hello", b"world"], [{}, {b"ck1": b"cv1", b"ck2": b"cv2"}])
    )
)
async def raw_command(request, server, client):
    command, command_arguments = request.param
    task = asyncio.create_task(client._raw_command(command, command_arguments))
    tag, server_command, server_command_arguments = await server.get_command()
    assert (server_command, server_command_arguments) == (command, command_arguments)
    return tag, task


@pytest.fixture
def curve_keys():
    return bridgeprotocol.CurveKeys(
        serverkey="rq:rM>}U?@Lns47E1%kR.o@n%FcmmsL/@{H8]yf7",
        publickey="Yne@$w-vo<fVvi]a<NY6T1ed:M$fCG*[IaLV{hID",
        secretkey="D:)Q[IlAW!ahhC2ac:9*A}h:p?([4%wOTJ%JR%cs",
    )


@pytest.fixture
def game_id():
    return uuid.uuid4()


@pytest.fixture
def game_kwargs(game_id):
    return {
        "game": game_id,
        "args": [1, 2, 3],
    }


@pytest.fixture
def game_and_player(game_id):
    return {
        "game": game_id,
        "player": uuid.uuid4(),
    }


@pytest.fixture
def join_kwargs(game_and_player):
    kwargs = {"position": _any_position()}
    kwargs.update(game_and_player)
    return kwargs


async def _event_generator_helper(event_receiver, factory):
    gen = factory()
    try:
        yield gen
    finally:
        event_receiver.close()
        with pytest.raises(StopAsyncIteration):
            await gen.__anext__()


async def _command_helper(
    server,
    client,
    command,
    *,
    expected_command,
    expected_command_args={},
    reply_args={},
):
    task = asyncio.create_task(command)
    tag, server_command, server_command_arguments = await server.get_command()
    assert (server_command, server_command_arguments) == (
        expected_command,
        client._serialize_all(expected_command_args),
    )
    await server.reply(tag, b"OK", client._serialize_all(reply_args))
    return await task


def _any_position():
    return random.choice(list(models.Position))


def _any_card():
    return models.CardType(
        rank=random.choice(list(models.Rank)), suit=random.choice(list(models.Suit)),
    )


def _any_bid():
    return models.Bid(
        level=random.randint(1, 7), strain=random.choice(list(models.Strain)),
    )


def _any_deal():
    # This isn't valid bridge deal state but... whatever
    return models.Deal(
        phase=random.choice(list(models.DealPhase)),
        positionInTurn=_any_position(),
        calls=[
            models.PositionCallPair(
                position=_any_position(),
                call=models.Call(type=models.CallType.bid, bid=_any_bid()),
            ),
            models.PositionCallPair(
                position=_any_position(), call=models.Call(type=models.CallType.pass_),
            ),
        ],
        declarer=_any_position(),
        contract=models.Contract(bid=_any_bid(), doubling=models.Doubling.redoubled),
        cards=models.CardsInHands(north=[_any_card(), _any_card()], east=[None, None]),
        tricks=[
            models.Trick(
                cards=[
                    models.PositionCardPair(position=_any_position(), card=_any_card())
                    for i in range(3)
                ],
                winner=_any_position(),
            )
            for j in range(3)
        ],
        vulnerability=models.Vulnerability(northSouth=True, eastWest=False),
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("reply_arguments", [{}, {b"rk1": b"rv1", b"rk2": b"rv2"}])
async def test_successful_command_should_return_with_reply_arguments(
    server, raw_command, reply_arguments
):
    tag, task = raw_command
    await server.reply(tag, b"OK", reply_arguments)
    assert await task == reply_arguments


@pytest.mark.asyncio
@pytest.mark.parametrize("reply_arguments", [{}, {b"rk1": b"rv1", b"rk2": b"rv2"}])
async def test_failed_command_should_raise_exception(
    server, raw_command, reply_arguments
):
    tag, task = raw_command
    await server.reply(tag, b"ERR", reply_arguments)
    with pytest.raises(bridgeprotocol.CommandFailure):
        await task


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error",
    [
        (b"NF", bridgeprotocol.NotFoundError),
        (b"AE", bridgeprotocol.AlreadyExistsError),
        (b"NA", bridgeprotocol.NotAuthorizedError),
        (b"SR", bridgeprotocol.SeatReservedError),
        (b"RV", bridgeprotocol.RuleViolationError),
    ],
)
async def test_failed_command_should_raise_exception_with_error_code(
    server, raw_command, error
):
    tag, task = raw_command
    error_code, exception_type = error
    await server.reply(tag, b"ERR:" + error_code, {})
    with pytest.raises(exception_type):
        await task


@pytest.mark.asyncio
async def test_client_with_curve(zmq_ctx, tmpdir, curve_keys):
    command = b"command"
    with mocks.MockBridgeServer(
        zmq_ctx, tmpdir, secretkey="JTKVSB%%)wK0E.X)V>+}o?pNmC{O&4W4b!Ni{Lh6"
    ) as server:
        with bridgeprotocol.BridgeClient(
            zmq_ctx, server.endpoint, curve_keys=curve_keys
        ) as client:
            task = asyncio.create_task(client._raw_command(command, {}))
            _, server_command, _ = await server.get_command()
            assert server_command == command
            task.cancel()


@pytest.mark.asyncio
async def test_client_should_handle_out_of_order_replies(server, client):
    command = b"command"
    status = b"OK"
    command_arguments = [{b"arg": value} for value in [b"value1", b"value2", b"value3"]]
    tasks = []
    tags = []
    # Send commands, then receive replies to them in reverse order
    for command_argument in command_arguments:
        tasks.append(
            asyncio.create_task(client._raw_command(command, command_argument))
        )
        tag, _, _ = await server.get_command()
        tags.append(tag)
    for task, tag, command_argument in reversed(
        list(zip(tasks, tags, command_arguments))
    ):
        await server.reply(tag, status, command_argument)
        assert await task == command_argument


@pytest.mark.asyncio
async def test_reply_missing_status_should_raise_error(server, raw_command):
    tag, task = raw_command
    await server.send(tag)
    with pytest.raises(bridgeprotocol.InvalidMessage):
        await task


@pytest.mark.asyncio
async def test_reply_with_odd_number_of_reply_argument_frames_should_raise_error(
    server, raw_command
):
    tag, task = raw_command
    await server.send(tag, b"OK", b"arg")
    with pytest.raises(bridgeprotocol.InvalidMessage):
        await task


@pytest.mark.asyncio
async def test_bridge_client_hello_command(server, client):
    assert (
        await _command_helper(
            server,
            client,
            client.hello(),
            expected_command=b"bridgehlo",
            expected_command_args={"version": "0.1", "role": "client"},
        )
        is None
    )


@pytest.mark.asyncio
async def test_bridge_client_game_command(server, client, game_kwargs):
    assert (
        await _command_helper(
            server,
            client,
            client.game(**game_kwargs),
            expected_command=b"game",
            expected_command_args=game_kwargs,
            reply_args={"game": game_kwargs["game"]},
        )
        == game_kwargs["game"]
    )


@pytest.mark.asyncio
async def test_bridge_client_game_command_should_fail_if_reply_missing_game(
    server, client, game_kwargs
):
    with pytest.raises(bridgeprotocol.ProtocolError):
        await _command_helper(
            server,
            client,
            client.game(**game_kwargs),
            expected_command=b"game",
            expected_command_args=game_kwargs,
        )


@pytest.mark.asyncio
async def test_bridge_client_game_command_should_fail_if_reply_has_invalid_type(
    server, client, game_kwargs
):
    with pytest.raises(bridgeprotocol.ProtocolError):
        await _command_helper(
            server,
            client,
            client.game(**game_kwargs),
            expected_command=b"game",
            expected_command_args=game_kwargs,
            reply_args={"game": 123},
        )


@pytest.mark.asyncio
async def test_bridge_client_join_command(server, client, join_kwargs):
    assert (
        await _command_helper(
            server,
            client,
            client.join(**join_kwargs),
            expected_command=b"join",
            expected_command_args=join_kwargs,
            reply_args={"game": join_kwargs["game"]},
        )
        == join_kwargs["game"]
    )


@pytest.mark.asyncio
async def test_bridge_client_join_command_should_fail_if_reply_missing_game(
    server, client, join_kwargs
):
    with pytest.raises(bridgeprotocol.ProtocolError):
        await _command_helper(
            server,
            client,
            client.join(**join_kwargs),
            expected_command=b"join",
            expected_command_args=join_kwargs,
        )


@pytest.mark.asyncio
async def test_bridge_client_join_command_should_fail_if_reply_has_invalid_type(
    server, client, join_kwargs
):
    with pytest.raises(bridgeprotocol.ProtocolError):
        await _command_helper(
            server,
            client,
            client.join(**join_kwargs),
            expected_command=b"join",
            expected_command_args=join_kwargs,
            reply_args={"game": 123},
        )


@pytest.mark.asyncio
async def test_bridge_client_leave_command(server, client, game_and_player):
    assert (
        await _command_helper(
            server,
            client,
            client.leave(**game_and_player),
            expected_command=b"leave",
            expected_command_args=game_and_player,
            reply_args={},
        )
        is None
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "call",
    [
        models.Call(type="pass", bid=None),
        models.Call(type="bid", bid=models.Bid(strain=models.Strain.notrump, level=3)),
    ],
)
async def test_bridge_client_call_command(server, client, call):
    kwargs = {
        "game": uuid.uuid4(),
        "player": uuid.uuid4(),
        "call": call,
    }
    assert (
        await _command_helper(
            server,
            client,
            client.call(**kwargs),
            expected_command=b"call",
            expected_command_args=kwargs,
        )
        is None
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "card",
    [
        models.CardType(rank=models.Rank.two, suit=models.Suit.clubs),
        models.CardType(rank=models.Rank.ace, suit=models.Suit.spades),
    ],
)
async def test_bridge_client_play_command(server, client, card):
    kwargs = {
        "game": uuid.uuid4(),
        "player": uuid.uuid4(),
        "card": card,
    }
    assert (
        await _command_helper(
            server,
            client,
            client.play(**kwargs),
            expected_command=b"play",
            expected_command_args=kwargs,
        )
        is None
    )


@pytest.mark.asyncio
async def test_get_game_success(server, client, game_and_player):
    deal = models.Deal()
    pubstate = deal.dict()
    pubstate["deal"] = str(pubstate.pop("id"))
    privstate = {}
    self = models.PlayerState(position=models.Position.north)
    results = [models.DealResult(deal=deal.id)]
    players = models.PlayersInGame(north=game_and_player["player"])
    game = models.Game(
        id=game_and_player["game"],
        deal=deal,
        self=self,
        results=results,
        players=players,
    )
    assert await _command_helper(
        server,
        client,
        client.get_game(**game_and_player),
        expected_command=b"get",
        expected_command_args=dict(
            **game_and_player,
            get=["pubstate", "privstate", "self", "results", "players"],
        ),
        reply_args={
            "get": {
                "pubstate": pubstate,
                "privstate": privstate,
                "self": self,
                "results": results,
                "players": players,
            },
            "counter": 123,
        },
    ) == (game, 123)


@pytest.mark.asyncio
@pytest.mark.parametrize("pubstate", [_any_deal(), _any_deal()])
@pytest.mark.parametrize(
    "privstate", [{"cards": {}}, {"cards": {"east": [_any_card(), _any_card()]}},],
)
class TestBridgeClientGetGameDealCommand:
    async def test_success(self, server, client, game_and_player, pubstate, privstate):
        deal = copy.deepcopy(pubstate)
        if cards_east := privstate["cards"].get("east"):
            deal.cards.east = copy.deepcopy(cards_east)
        pubstate = pubstate.dict()
        pubstate["deal"] = str(pubstate.pop("id"))
        assert await _command_helper(
            server,
            client,
            client.get_game_deal(**game_and_player),
            expected_command=b"get",
            expected_command_args=dict(
                **game_and_player, get=["pubstate", "privstate"]
            ),
            reply_args={
                "get": {"pubstate": pubstate, "privstate": privstate},
                "counter": 123,
            },
        ) == (deal, 123)

    async def test_missing_pubstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_game_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"privstate": privstate}, "counter": 123},
            )

    async def test_invalid_pubstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        # pubstate is invalid if we don't do the preprosessing here
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_game_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={
                    "get": {"pubstate": pubstate, "privstate": privstate},
                    "counter": 123,
                },
            )

    async def test_missing_privstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        pubstate = pubstate.dict()
        pubstate["deal"] = str(pubstate.pop("id"))
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_game_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"pubstate": pubstate, "counter": 123}},
            )

    async def test_invalid_privstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        pubstate = pubstate.dict()
        pubstate["deal"] = str(pubstate.pop("id"))
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_game_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={
                    "get": {"pubstate": pubstate, "privstate": "invalid"},
                    "counter": 123,
                },
            )

    async def test_missing_counter_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        pubstate = pubstate.dict()
        pubstate["deal"] = str(pubstate.pop("id"))
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_game_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"pubstate": pubstate, "privstate": privstate}},
            )

    async def test_invalid_counter_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        pubstate = pubstate.dict()
        pubstate["deal"] = str(pubstate.pop("id"))
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_game_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={
                    "get": {"pubstate": pubstate, "privstate": privstate},
                    "counter": "invalid",
                },
            )


@pytest.mark.asyncio
@pytest.mark.parametrize("pubstate", [_any_deal(), _any_deal()])
class TestBridgeClientGetDealCommand:
    async def test_success(self, server, client, pubstate):
        deal = copy.deepcopy(pubstate)
        pubstate = pubstate.dict()
        pubstate["deal"] = str(pubstate.pop("id"))
        assert (
            await _command_helper(
                server,
                client,
                client.get_deal(deal=deal.id),
                expected_command=b"get",
                expected_command_args=dict(deal=deal.id),
                reply_args={"get": {"pubstate": pubstate}},
            )
            == deal
        )

    async def test_missing_pubstate_should_lead_to_failure(
        self, server, client, pubstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_deal(deal=pubstate.id),
                expected_command=b"get",
                expected_command_args=dict(deal=pubstate.id),
                reply_args={"get": {}},
            )

    async def test_invalid_pubstate_should_lead_to_failure(
        self, server, client, pubstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_deal(deal=pubstate.id),
                expected_command=b"get",
                expected_command_args=dict(deal=pubstate.id),
                reply_args={"get": {"pubstate": "invalid"}},
            )


@pytest.mark.asyncio
async def test_null_deal(server, client, game_and_player):
    assert await _command_helper(
        server,
        client,
        client.get_game_deal(**game_and_player),
        expected_command=b"get",
        expected_command_args=dict(**game_and_player, get=["pubstate", "privstate"]),
        reply_args={"get": {"pubstate": None, "privstate": None}, "counter": 123},
    ) == (None, 123)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "self_",
    [
        models.PlayerState(),
        models.PlayerState(
            position=_any_position(),
            allowedCalls=[
                models.Call(type=models.CallType.pass_),
                models.Call(type=models.CallType.bid, bid=_any_bid()),
            ],
            allowedCards=[_any_card(), _any_card()],
        ),
    ],
)
class TestBridgeClientGetSelfCommand:
    async def test_success(self, server, client, game_and_player, self_):
        assert await _command_helper(
            server,
            client,
            client.get_self(**game_and_player),
            expected_command=b"get",
            expected_command_args=dict(**game_and_player, get=["self"]),
            reply_args={"get": {"self": self_}, "counter": 123},
        ) == (self_, 123)

    async def test_missing_self_should_lead_to_failure(
        self, server, client, game_and_player, self_
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_self(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(**game_and_player, get=["self"]),
                reply_args={"get": {}, "counter": 123},
            )

    async def test_invalid_self_should_lead_to_failure(
        self, server, client, game_and_player, self_
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_self(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(**game_and_player, get=["self"]),
                reply_args={"get": {"self": "invalid"}, "counter": 123},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "results",
    [
        [],
        [
            models.DealResult(
                deal=uuid.uuid4(),
                result=models.DuplicateResult(
                    partnership=models.Partnership.northSouth, score=100
                ),
            ),
            models.DealResult(deal=uuid.uuid4(), result=None),
        ],
    ],
)
class TestBridgeClientGetResultsCommand:
    async def test_success(self, server, client, game_id, results):
        assert await _command_helper(
            server,
            client,
            client.get_results(game=game_id),
            expected_command=b"get",
            expected_command_args={"game": game_id, "get": ["results"]},
            reply_args={
                "get": {
                    "results": [
                        {"deal": result.deal, "result": result.result}
                        for result in results
                    ]
                },
                "counter": 123,
            },
        ) == (results, 123)

    async def test_missing_results_should_lead_to_failure(
        self, server, client, game_id, results
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_results(game=game_id),
                expected_command=b"get",
                expected_command_args={"game": game_id, "get": ["results"]},
                reply_args={"get": {}, "counter": 123},
            )

    async def test_invalid_results_should_lead_to_failure(
        self, server, client, game_id, results
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_results(game=game_id),
                expected_command=b"get",
                expected_command_args={"game": game_id, "get": ["results"]},
                reply_args={"get": {"results": "invalid"}, "counter": 123},
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "players",
    [
        models.PlayersInGame(),
        models.PlayersInGame(
            north=uuid.uuid4(),
            east=uuid.uuid4(),
            south=uuid.uuid4(),
            west=uuid.uuid4(),
        ),
    ],
)
class TestBridgeClientGetPlayersCommand:
    async def test_success(self, server, client, game_id, players):
        assert await _command_helper(
            server,
            client,
            client.get_players(game=game_id),
            expected_command=b"get",
            expected_command_args={"game": game_id, "get": ["players"]},
            reply_args={"get": {"players": players.dict()}, "counter": 123},
        ) == (players, 123)

    async def test_missing_players_should_lead_to_failure(
        self, server, client, game_id, players
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_players(game=game_id),
                expected_command=b"get",
                expected_command_args={"game": game_id, "get": ["players"]},
                reply_args={"get": {}, "counter": 123},
            )

    async def test_invalid_players_should_lead_to_failure(
        self, server, client, game_id, players
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_players(game=game_id),
                expected_command=b"get",
                expected_command_args={"game": game_id, "get": ["players"]},
                reply_args={"get": {"players": "invalid"}, "counter": 123},
            )


@pytest.mark.asyncio
async def test_bridge_client_retry_handshake(server, client, join_kwargs):
    task = asyncio.create_task(client.join(**join_kwargs))
    tag, server_command, server_command_arguments = await server.get_command()
    assert server_command == b"join"
    await server.reply(tag, b"ERR:UNK", {})
    tag, server_command, server_command_arguments = await server.get_command()
    assert server_command == b"bridgehlo"
    await server.reply(tag, b"OK", {})
    tag, server_command, server_command_arguments = await server.get_command()
    assert server_command == b"join"
    reply_args = {"game": join_kwargs["game"]}
    await server.reply(tag, b"OK", client._serialize_all(reply_args))
    return await task


@pytest.mark.asyncio
@pytest.mark.parametrize("event_tag", [b"hello", b"world"])
@pytest.mark.parametrize("event_arguments", [{}, {b"arg": b"value"}])
async def test_event_receiver_base(server, event_receiver, event_tag, event_arguments):
    await server.send_event(event_tag, event_arguments)
    assert await event_receiver._get_raw_event() == (event_tag, event_arguments)


@pytest.mark.asyncio
async def test_event_with_odd_number_of_argument_frames_should_raise_error(
    server, event_receiver
):
    server._event_socket.send_multipart([b"tag", b"key"])
    with pytest.raises(bridgeprotocol.InvalidMessage):
        await event_receiver._get_raw_event()


@pytest.mark.asyncio
async def test_event_receiver_with_curve(zmq_ctx, tmpdir, curve_keys):
    event = b"event"
    with mocks.MockBridgeServer(
        zmq_ctx, tmpdir, secretkey="JTKVSB%%)wK0E.X)V>+}o?pNmC{O&4W4b!Ni{Lh6"
    ) as server:
        with bridgeprotocol.BridgeEventReceiver(
            zmq_ctx, server.event_endpoint, curve_keys=curve_keys
        ) as event_receiver:
            # Establishing a pub-sub connection happens
            # asynchronously. Waiting for a while is required for this
            # test case to success. Could this be made less flaky?
            await asyncio.sleep(0.03)
            await server.send_event(event, {})
            assert await event_receiver._get_raw_event() == (event, {})


@pytest.mark.asyncio
@pytest.mark.parametrize("event_type", ["event1", "event2"])
@pytest.mark.parametrize("event_arguments", [{}, {"key": "value", "pi": 3.14}])
class TestEventReceiver:
    async def test_bridge_event_receiver_get_event(
        self, server, client, event_receiver, event_type, event_arguments
    ):
        game_id = uuid.uuid4()
        await server.send_event(
            f"{str(game_id)}:{event_type}".encode(),
            client._serialize_all(event_arguments),
        )
        assert await event_receiver.get_event() == bridgeprotocol.BridgeEvent(
            game=game_id, type=event_type, **event_arguments
        )

    async def test_invalid_event_from_generator_should_be_ignored_with_warning(
        self, server, client, event_generator, event_type, event_arguments, caplog
    ):
        game_id = uuid.uuid4()
        await server.send_event(b"invalid-tag", {})
        await server.send_event(
            f"{str(game_id)}:{event_type}".encode(),
            client._serialize_all(event_arguments),
        )
        assert await event_generator.__anext__() == bridgeprotocol.BridgeEvent(
            game=game_id, type=event_type, **event_arguments
        )
        assert [r.levelname for r in caplog.records] == ["WARNING"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "event_type,event_cls,event_arguments",
    [
        (
            "player",
            bridgeprotocol.events.PlayerEvent,
            {"position": _any_position(), "player": uuid.uuid4()},
        ),
        (
            "deal",
            bridgeprotocol.events.DealEvent,
            {
                "deal": uuid.uuid4(),
                "opener": _any_position(),
                "vulnerability": models.Vulnerability(),
            },
        ),
        (
            "turn",
            bridgeprotocol.events.TurnEvent,
            {"deal": uuid.uuid4(), "position": _any_position()},
        ),
        (
            "call",
            bridgeprotocol.events.CallEvent,
            {
                "deal": uuid.uuid4(),
                "position": _any_position(),
                "call": models.Call(type=models.CallType.pass_),
                "index": random.randint(0, 16),
            },
        ),
        (
            "bidding",
            bridgeprotocol.events.BiddingEvent,
            {
                "deal": uuid.uuid4(),
                "declarer": _any_position(),
                "contract": models.Contract(
                    bid=_any_bid(), doubling=models.Doubling.undoubled
                ),
            },
        ),
        (
            "play",
            bridgeprotocol.events.PlayEvent,
            {
                "deal": uuid.uuid4(),
                "position": _any_position(),
                "card": _any_card(),
                "trick": random.randint(0, 12),
                "index": random.randint(0, 3),
            },
        ),
        (
            "dummy",
            bridgeprotocol.events.DummyEvent,
            {
                "deal": uuid.uuid4(),
                "position": _any_position(),
                "cards": [_any_card(), _any_card()],
            },
        ),
        (
            "trick",
            bridgeprotocol.events.TrickEvent,
            {
                "deal": uuid.uuid4(),
                "winner": _any_position(),
                "index": random.randint(0, 12),
            },
        ),
        (
            "dealend",
            bridgeprotocol.events.DealEndEvent,
            {"deal": uuid.uuid4(), "result": models.DuplicateResult()},
        ),
    ],
)
async def test_bridge_event_receiver_concrete_events(
    server, client, event_receiver, game_id, event_type, event_cls, event_arguments
):
    await server.send_event(
        f"{str(game_id)}:{event_type}".encode(), client._serialize_all(event_arguments)
    )
    assert await event_receiver.get_event() == event_cls(
        game=game_id,
        type=bridgeprotocol.events.EventType[event_type],
        **event_arguments,
    )


@pytest.mark.parametrize(
    "target,patch,result",
    [
        ({"a": "b"}, {"a": "c"}, {"a": "c"}),
        ({"a": "b"}, {"b": "c"}, {"a": "b", "b": "c"}),
        ({"a": "b"}, {"a": None}, {}),
        ({"a": "b", "b": "c"}, {"a": None}, {"b": "c"}),
        ({"a": ["b"]}, {"a": "c"}, {"a": "c"}),
        ({"a": "c"}, {"a": ["b"]}, {"a": ["b"]}),
        ({"a": {"b": "c"}}, {"a": {"b": "d", "c": None}}, {"a": {"b": "d"}}),
        ({"a": [{"b": "c"}]}, {"a": [1]}, {"a": [1]}),
        (["a", "b"], ["c", "d"], ["c", "d"]),
        ({"a": "b"}, ["c"], ["c"]),
        ({"a": "foo"}, None, None),
        ({"a": "foo"}, "bar", "bar"),
        ({"e": None}, {"a": 1}, {"e": None, "a": 1}),
        ([1, 2], {"a": "b", "c": None}, {"a": "b"}),
        ({}, {"a": {"bb": {"ccc": None}}}, {"a": {"bb": {}}}),
    ],
)
def test_merge_patch(target, patch, result):
    """JSON Merge Patch example test cases from RFC 7396"""
    assert bridgeprotocol.utils.merge_patch(target, patch) == result


@pytest.mark.parametrize(
    "control_endpoint,event_endpoint",
    [
        ("tcp://localhost:5555", "tcp://localhost:5556"),
        ("tcp://example.com:1234", "tcp://example.com:1235"),
    ],
)
def test_endpoints(control_endpoint, event_endpoint):
    assert bridgeprotocol.utils.endpoints(control_endpoint) == (
        control_endpoint,
        event_endpoint,
    )


@pytest.mark.parametrize(
    "control_endpoint", ["inproc://wrong.endpoint", "tcp://localhost:not-a-port"]
)
def test_endpoints_should_fail_if_control_endpoint_has_wrong_format(control_endpoint):
    with pytest.raises(ValueError):
        bridgeprotocol.utils.endpoints(control_endpoint)
