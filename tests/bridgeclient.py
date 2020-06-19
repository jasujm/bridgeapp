"""Test client that sends as much traffic to a bridge server as possible"""

import asyncio
import contextlib
import random
import uuid

import click
import click_log
import zmq.asyncio

from bridgeapp import bridgeprotocol, models

click_log.basic_config()


async def _get_turn_from_deal_state(client, game, player):
    deal_state = await client.get_deal(game=game, player=player)
    return deal_state.positionInTurn


async def _get_turn_from_events(event_receiver):
    async for event in event_receiver.events():
        if event.type == "turn":
            return models.Position(event.position)


async def _play_bridge_game(
    client: bridgeprotocol.BridgeClient,
    event_receiver: bridgeprotocol.BridgeEventReceiver,
):
    player_uuids = {position: uuid.uuid4() for position in models.Position}
    player_uuid = player_uuids[models.Position.north]
    game_uuid = await client.game()
    for position, player_uuid in player_uuids.items():
        await client.join(game=game_uuid, player=player_uuid, position=position)
    position_in_turn = await _get_turn_from_deal_state(client, game_uuid, player_uuid)
    while True:
        player_uuid = player_uuids[position_in_turn]
        player_state = await client.get_player(game=game_uuid, player=player_uuid)
        if calls := player_state.allowedCalls:
            await client.call(
                game=game_uuid, player=player_uuid, call=random.choice(calls)
            )
        elif cards := player_state.allowedCards:
            await client.play(
                game=game_uuid, player=player_uuid, card=random.choice(cards)
            )
        try:
            position_in_turn = await asyncio.wait_for(
                _get_turn_from_events(event_receiver), timeout=0.1
            )
        except asyncio.TimeoutError:
            position_in_turn = await _get_turn_from_deal_state(
                client, game_uuid, player_uuid
            )


async def _async_main(control_endpoint, event_endpoint):
    ctx = zmq.asyncio.Context()
    try:
        with await bridgeprotocol.BridgeClient.create(
            ctx, control_endpoint
        ) as client, bridgeprotocol.BridgeEventReceiver(
            ctx, event_endpoint
        ) as event_receiver:
            await _play_bridge_game(client, event_receiver)
    finally:
        ctx.term()


@click.command()
@click_log.simple_verbosity_option()
@click.argument("control_endpoint")
@click.argument("event_endpoint")
def main(control_endpoint, event_endpoint):
    """Test client for the bridge backend

    This program is a client that opens a connection to the endpoints
    and plays arbitrary bridge games as fast as possible. Intended to
    be used for stress testing.
    """
    asyncio.run(_async_main(control_endpoint, event_endpoint))


if __name__ == "__main__":
    main()  # pylint: disable=no-value-for-parameter
