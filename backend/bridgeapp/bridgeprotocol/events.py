"""Event receiver"""

import asyncio
import enum
import functools
import typing
import uuid

import orjson
import pydantic

from . import _base, models


class EventType(enum.Enum):
    """Event type"""

    player = "player"
    deal = "deal"
    turn = "turn"
    call = "call"
    bidding = "bidding"
    play = "play"
    dummy = "dummy"
    trick = "trick"
    dealend = "dealend"


class BridgeEvent(pydantic.BaseModel):
    """Bridge event"""

    game: models.GameUuid
    type: typing.Union[EventType, str]
    counter: int = 0

    class Config:  # pylint: disable=all
        extra = "allow"


_EVENT_CLASSES: typing.Dict[str, typing.Type[BridgeEvent]] = {}


def _register_event(type: str):
    def decorator(cls):
        _EVENT_CLASSES[type] = cls
        return cls

    return decorator


@_register_event("player")
class PlayerEvent(BridgeEvent):
    """Player event

    Sent when a player joins or leaves a game."""

    position: models.Position
    player: typing.Optional[models.PlayerUuid]


@_register_event("deal")
class DealEvent(BridgeEvent):
    """Deal event

    Sent when a new deal starts."""

    deal: models.DealUuid
    opener: models.Position
    vulnerability: models.Vulnerability


@_register_event("turn")
class TurnEvent(BridgeEvent):
    """Turn event

    Sent when a new player gets a turn."""

    deal: models.DealUuid
    position: models.Position


@_register_event("call")
class CallEvent(BridgeEvent):
    """Call event

    Sent when a player makes a call"""

    deal: models.DealUuid
    position: models.Position
    call: models.Call
    index: int


@_register_event("bidding")
class BiddingEvent(BridgeEvent):
    """Bidding event

    Sent when a contract is reached."""

    deal: models.DealUuid
    declarer: models.Position
    contract: models.Contract


@_register_event("play")
class PlayEvent(BridgeEvent):
    """Play event

    Sent when a player plays a card"""

    deal: models.DealUuid
    position: models.Position
    card: models.CardType
    trick: int
    index: int


@_register_event("dummy")
class DummyEvent(BridgeEvent):
    """Dummy event

    Sent when the hand of the dummy is revealed."""

    deal: models.DealUuid
    position: models.Position
    cards: typing.List[models.CardType]


@_register_event("trick")
class TrickEvent(BridgeEvent):
    """Trick event

    Sent when a trick is completed."""

    deal: models.DealUuid
    winner: models.Position
    index: int


@_register_event("dealend")
class DealEndEvent(BridgeEvent):
    """Deal end event

    Sent when a deal is completed."""

    deal: models.DealUuid
    contract: typing.Optional[models.Contract]
    tricksWon: typing.Optional[int]
    result: models.DuplicateResult


assert set(type.name for type in EventType) == set(
    _EVENT_CLASSES.keys()
), "an expected event was not registered"


class BridgeEventReceiver(_base.EventReceiverBase):
    """Client for receiving events from a bridge backend server"""

    @staticmethod
    def _deserialize(arg):
        return orjson.loads(arg)

    @staticmethod
    def _create_event(tag: str, **kwargs) -> BridgeEvent:
        game, type = tag.split(":")
        cls = _EVENT_CLASSES.get(type, BridgeEvent)
        type = EventType.__members__.get(type, type)
        return cls(game=uuid.UUID(game), type=type, **kwargs)
