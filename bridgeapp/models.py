"""
Model definitions
-----------------

The :mod:`models` module contains the model definitions needed across
the application.
"""

import enum
import typing
import uuid

import pydantic

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use


class Position(enum.Enum):
    """Position of a bridge player"""

    north = "north"
    east = "east"
    south = "south"
    west = "west"


class CallType(enum.Enum):
    """Bridge call type"""

    pass_ = "pass"
    double = "double"
    redouble = "redouble"
    bid = "bid"


class Strain(enum.Enum):
    """Bridge bid strain"""

    clubs = "clubs"
    diamonds = "diamonds"
    hearts = "hearts"
    spades = "spades"
    notrump = "notrump"


class Bid(pydantic.BaseModel):
    """Bridge bid"""

    strain: Strain
    level: int

    @pydantic.validator("level")
    def _level_must_be_between_one_and_seven(cls, level):
        if not 1 <= level <= 7:
            raise ValueError("`level` must be between 1 and 7")
        return level


class Call(pydantic.BaseModel):
    """Call during bridge bidding phase"""

    type: CallType
    bid: typing.Optional[Bid]

    @pydantic.root_validator
    def _check_call_has_bid_iff_type_is_bid(cls, values):
        if bool(values["type"] == CallType.bid) == bool(values["bid"] is None):
            raise ValueError("Call must have `bid` if and only if its `type` is bid")
        return values


class Doubling(enum.Enum):
    """Doubling status of a bridge contract"""

    undoubled = "undoubled"
    doubled = "doubled"
    redoubled = "redoubled"


class Contract(pydantic.BaseModel):
    """Bridge contract"""

    bid: Bid
    doubling: Doubling


class Rank(enum.Enum):
    """Playing card rank"""

    two = "2"
    three = "3"
    four = "4"
    five = "5"
    six = "6"
    seven = "7"
    eight = "8"
    nine = "9"
    ten = "10"
    jack = "jack"
    queen = "queen"
    king = "king"
    ace = "ace"


class Suit(enum.Enum):
    """Playing card suit"""

    clubs = "clubs"
    diamonds = "diamonds"
    hearts = "hearts"
    spades = "spades"


class CardType(pydantic.BaseModel):
    """Playing card type"""

    rank: Rank
    suit: Suit


CardList = typing.List[typing.Optional[CardType]]
"""List of cards, either revealed or not revealed"""


class Cards(pydantic.BaseModel):
    """Cards in a bridge deal"""

    north: CardList = []
    east: CardList = []
    south: CardList = []
    west: CardList = []


class TricksWon(pydantic.BaseModel):
    """Trick tally by partnership"""

    northSouth: int = 0
    eastWest: int = 0


class Vulnerability(pydantic.BaseModel):
    """Vulnerability by partnership"""

    northSouth: bool = False
    eastWest: bool = False


class PositionCallPair(pydantic.BaseModel):
    """Position-call pair"""

    position: Position
    call: Call


class PositionCardPair(pydantic.BaseModel):
    """Position-card pair"""

    position: Position
    card: CardType


class DealState(pydantic.BaseModel):
    """Bridge deal state"""

    positionInTurn: typing.Optional[Position]
    calls: typing.List[PositionCallPair] = []
    declarer: typing.Optional[Position]
    contract: typing.Optional[Contract]
    cards: Cards = Cards()
    trick: typing.List[PositionCardPair] = []
    tricksWon: TricksWon = TricksWon()
    vulnerability: Vulnerability = Vulnerability()


class PlayerState(pydantic.BaseModel):
    """Player state within a bridge deal"""

    position: typing.Optional[Position]
    allowedCalls: typing.List[Call] = []
    allowedCards: typing.List[CardType] = []


class Game(pydantic.BaseModel):
    """Bridge game"""

    uuid: uuid.UUID


class Player(pydantic.BaseModel):
    """Player taking part in a bridge game"""

    uuid: uuid.UUID
