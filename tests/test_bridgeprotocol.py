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

from bridgeapp import bridgeprotocol, models
from . import mocks


@pytest.fixture
def zmq_ctx():
    """Yield ZeroMQ context"""
    ctx = zmq.asyncio.Context()
    yield ctx
    ctx.term()


@pytest.fixture
def server(zmq_ctx):
    """Yield a :class:`mocks.MockBridgeServer` instance"""
    with mocks.MockBridgeServer(zmq_ctx) as srv:
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
def game_kwargs():
    return {
        "game": uuid.uuid4(),
        "args": [1, 2, 3],
    }


@pytest.fixture
def game_and_player():
    return {
        "game": uuid.uuid4(),
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
@pytest.mark.parametrize("keys", [[], ["key1", "key2"]])
@pytest.mark.parametrize("response", [{}, {"key1": "value1", "key2": "value2"}])
async def test_bridge_client_get_command(
    server, client, game_and_player, keys, response
):
    kwargs = dict(get=keys, **game_and_player)
    assert (
        await _command_helper(
            server,
            client,
            client.get(**kwargs),
            expected_command=b"get",
            expected_command_args=kwargs,
            reply_args={"get": response},
        )
        == response
    )


@pytest.mark.asyncio
async def test_bridge_client_get_command_should_fail_if_reply_missing_get(
    server, client, game_and_player
):
    kwargs = dict(get=[], **game_and_player)
    with pytest.raises(bridgeprotocol.InvalidMessage):
        await _command_helper(
            server,
            client,
            client.get(**kwargs),
            expected_command=b"get",
            expected_command_args=kwargs,
        )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "pubstate",
    [
        models.DealState(),
        # This isn't valid bridge deal state but... whatever
        models.DealState(
            positionInTurn=_any_position(),
            calls=[
                models.PositionCallPair(
                    position=_any_position(),
                    call=models.Call(type=models.CallType.bid, bid=_any_bid()),
                ),
                models.PositionCallPair(
                    position=_any_position(),
                    call=models.Call(type=models.CallType.pass_),
                ),
            ],
            declarer=_any_position(),
            contract=models.Contract(
                bid=_any_bid(), doubling=models.Doubling.redoubled
            ),
            cards=models.Cards(north=[_any_card(), _any_card()], east=[None, None],),
            tricks=[
                models.PositionCardPair(position=_any_position(), card=_any_card(),)
                for i in range(3)
            ],
            tricksWon=models.TricksWon(
                northSouth=random.randint(1, 6), eastWest=random.randint(1, 6),
            ),
            vulnerability=models.Vulnerability(northSouth=True, eastWest=False,),
        ),
    ],
)
@pytest.mark.parametrize(
    "privstate", [{"cards": {}}, {"cards": {"east": [_any_card(), _any_card()]}},],
)
class TestBridgeClientGetDealCommand:
    async def test_success(self, server, client, game_and_player, pubstate, privstate):
        deal_state = copy.deepcopy(pubstate)
        if cards_east := privstate["cards"].get("east"):
            deal_state.cards.east = copy.deepcopy(cards_east)
        assert (
            await _command_helper(
                server,
                client,
                client.get_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"pubstate": pubstate, "privstate": privstate}},
            )
            == deal_state
        )

    async def test_missing_pubstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"privstate": privstate}},
            )

    async def test_invalid_pubstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"pubstate": "invalid", "privstate": privstate}},
            )

    async def test_missing_privstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"pubstate": pubstate}},
            )

    async def test_invalid_privstate_should_lead_to_failure(
        self, server, client, game_and_player, pubstate, privstate
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_deal(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(
                    **game_and_player, get=["pubstate", "privstate"]
                ),
                reply_args={"get": {"pubstate": pubstate, "privstate": "invalid"}},
            )


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
class TestBridgeClientGetPlayerCommand:
    async def test_success(self, server, client, game_and_player, self_):
        assert (
            await _command_helper(
                server,
                client,
                client.get_player(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(**game_and_player, get=["self"]),
                reply_args={"get": {"self": self_}},
            )
            == self_
        )

    async def test_missing_self_should_lead_to_failure(
        self, server, client, game_and_player, self_
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_player(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(**game_and_player, get=["self"]),
                reply_args={"get": {}},
            )

    async def test_invalid_self_should_lead_to_failure(
        self, server, client, game_and_player, self_
    ):
        with pytest.raises(bridgeprotocol.InvalidMessage):
            await _command_helper(
                server,
                client,
                client.get_player(**game_and_player),
                expected_command=b"get",
                expected_command_args=dict(**game_and_player, get=["self"]),
                reply_args={"get": {"self": "invalid"}},
            )


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
@pytest.mark.parametrize("event_type", ["event1", "event2"])
@pytest.mark.parametrize("event_arguments", [{}, {"key": "value", "pi": 3.14}])
class TestEventReceiver:
    async def test_bridge_event_receiver_get_event(
        self, server, client, event_receiver, event_type, event_arguments
    ):
        game_uuid = uuid.uuid4()
        await server.send_event(
            f"{str(game_uuid)}:{event_type}".encode(),
            client._serialize_all(event_arguments),
        )
        assert await event_receiver.get_event() == bridgeprotocol.BridgeEvent(
            game=game_uuid, type=event_type, **event_arguments
        )

    async def test_invalid_event_from_generator_should_be_ignored_with_warning(
        self, server, client, event_generator, event_type, event_arguments, caplog
    ):
        game_uuid = uuid.uuid4()
        await server.send_event(b"invalid-tag", {})
        await server.send_event(
            f"{str(game_uuid)}:{event_type}".encode(),
            client._serialize_all(event_arguments),
        )
        assert await event_generator.__anext__() == bridgeprotocol.BridgeEvent(
            game=game_uuid, type=event_type, **event_arguments
        )
        assert [r.levelname for r in caplog.records] == ["WARNING"]


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
