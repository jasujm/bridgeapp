"""Test client that sends as much traffic to a bridge server as possible"""

import asyncio
import contextlib
import random
import uuid

import click
import zmq.asyncio

from bridgeapp import bridgeprotocol, models


async def _play_bridge_game(
    client: bridgeprotocol.BridgeClient,
    event_receiver: bridgeprotocol.BridgeEventReceiver,
):
    player_uuids = {position: uuid.uuid4() for position in models.Position}
    game_uuid = await client.game()
    for position, player_uuid in player_uuids.items():
        await client.join(game=game_uuid, player=player_uuid, position=position)
    async for event in event_receiver.events():
        if event.type == "turn":
            position_in_turn = models.Position(event.position)
            player_uuid = player_uuids[position_in_turn]
            player_state = await client.get_player(game=game_uuid, player=player_uuid)
            with contextlib.suppress(bridgeprotocol.CommandFailure):
                if calls := player_state.allowedCalls:
                    await client.call(
                        game=game_uuid, player=player_uuid, call=random.choice(calls)
                    )
                elif cards := player_state.allowedCards:
                    await client.play(
                        game=game_uuid, player=player_uuid, card=random.choice(cards)
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
