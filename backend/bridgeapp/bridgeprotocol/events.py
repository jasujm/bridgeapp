"""Bridge event receiver"""

import asyncio
import uuid

import orjson
import pydantic

from . import _base


class BridgeEvent(pydantic.BaseModel):
    """Bridge event"""

    game: uuid.UUID
    type: str

    class Config:  # pylint: disable=all
        extra = "allow"


class BridgeEventReceiver(_base.EventReceiverBase):
    """Client for receiving events from a bridge backend server"""

    @staticmethod
    def _deserialize(arg):
        return orjson.loads(arg)

    @staticmethod
    def _create_event(tag: str, **kwargs) -> BridgeEvent:
        game, type = tag.split(":")
        return BridgeEvent(game=uuid.UUID(game), type=type, **kwargs)

    async def subscribe(game_uuid: uuid.UUID):
        while True:
            yield BridgeEvent(game=game_uuid, type="dummy")
            await asyncio.sleep(1)
