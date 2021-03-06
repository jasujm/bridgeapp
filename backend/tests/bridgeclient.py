"""Test client that sends as much traffic to a bridge server as possible"""

import asyncio
import contextlib
import logging
import random
import sys
import typing
import uuid

import click
import click_log
import zmq.asyncio

from bridgeapp import bridgeprotocol, settings
from bridgeapp.bridgeprotocol import models

click_log.basic_config()
logger = logging.getLogger(__name__)


async def _wreak_havoc(client: bridgeprotocol.BridgeClient, game_id: uuid.UUID):
    # Wreak minor havoc by trying to do illegal moves
    player_id = uuid.uuid4()
    while True:
        await asyncio.sleep(0.1)
        with contextlib.suppress(bridgeprotocol.CommandFailure):
            await client.call(
                game=game_id,
                player=player_id,
                call=models.Call(type=models.CallType.pass_),
            )
            logger.error("Havoc wreaked")
            sys.exit(1)
        with contextlib.suppress(bridgeprotocol.CommandFailure):
            await client.play(
                game=game_id,
                player=player_id,
                card=models.CardType(
                    rank=random.choice(list(models.Rank)),
                    suit=random.choice(list(models.Suit)),
                ),
            )
            logger.error("Havoc wreaked")
            sys.exit(1)


async def _get_results(client: bridgeprotocol.BridgeClient, game_id: uuid.UUID):
    while True:
        await asyncio.sleep(2)
        results, counter = await client.get_results(game=game_id)
        logger.info("Deal results: %r, counter: %d", results, counter)


async def _get_turn_from_deal(client, game, player):
    deal, _ = await client.get_game_deal(game=game, player=player)
    return deal.positionInTurn


async def _get_turn_from_events(event_receiver):
    async for event in event_receiver.events():
        if event.type == "turn":
            return models.Position(event.position)


async def _change_players(
    client: bridgeprotocol.BridgeClient,
    player_ids: typing.Mapping[models.Position, uuid.UUID],
    game_id: uuid.UUID,
):
    new_player_ids = {}
    for position, player_id in player_ids.items():
        await client.leave(game=game_id, player=player_id)
        new_player_id = uuid.uuid4()
        new_player_ids[position] = new_player_id
        await client.join(game=game_id, player=new_player_id, position=position)
    return new_player_ids


def _alarm_task():
    return asyncio.create_task(asyncio.sleep(1))


async def _play_bridge_game(
    client: bridgeprotocol.BridgeClient,
    event_receiver: bridgeprotocol.BridgeEventReceiver,
    game_id: uuid.UUID,
):
    player_ids = {position: uuid.uuid4() for position in models.Position}
    for position, player_id in player_ids.items():
        await client.join(game=game_id, player=player_id, position=position)
    players_in_game, _ = await client.get_players(game=game_id)
    logger.info("Players in the game: %r", players_in_game)
    position_in_turn = await _get_turn_from_deal(client, game_id, player_id)
    alarm = _alarm_task()
    while True:
        if alarm.done():
            await alarm
            player_ids = await _change_players(client, player_ids, game_id)
            alarm = _alarm_task()
        player_id = player_ids[position_in_turn]
        player_state, _ = await client.get_self(game=game_id, player=player_id)
        if calls := player_state.allowedCalls:
            await client.call(game=game_id, player=player_id, call=random.choice(calls))
        elif cards := player_state.allowedCards:
            await client.play(game=game_id, player=player_id, card=random.choice(cards))
        try:
            position_in_turn = await asyncio.wait_for(
                _get_turn_from_events(event_receiver), timeout=0.1
            )
        except asyncio.TimeoutError:
            position_in_turn = await _get_turn_from_deal(client, game_id, player_id)


async def _async_main(
    endpoint: str, *, curve_keys: typing.Optional[bridgeprotocol.CurveKeys] = None
):
    control_endpoint, event_endpoint = bridgeprotocol.utils.endpoints(endpoint)
    ctx = zmq.asyncio.Context()
    try:
        with await bridgeprotocol.BridgeClient.create(
            ctx, control_endpoint, curve_keys=curve_keys
        ) as client, bridgeprotocol.BridgeEventReceiver(
            ctx, event_endpoint, curve_keys=curve_keys
        ) as event_receiver:
            game_id = await client.game()
            await asyncio.wait(
                [
                    asyncio.create_task(_wreak_havoc(client, game_id)),
                    asyncio.create_task(_get_results(client, game_id)),
                    asyncio.create_task(
                        _play_bridge_game(client, event_receiver, game_id)
                    ),
                ]
            )
    finally:
        ctx.term()


@click.command()
@click_log.simple_verbosity_option()
@click.argument("endpoint", required=False)
def main(endpoint):
    """Test client for the bridge backend

    This program is a client that connects to a bridge backend at
    ENDPOINT and plays arbitrary bridge games as fast as
    possible. Intended to be used for stress testing.
    """
    defaults = {"backend_endpoint": endpoint} if endpoint else {}
    s = settings.get_settings(**defaults)
    asyncio.run(_async_main(s.backend_endpoint, curve_keys=s.curve_keys))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
