"""
Models
......
"""

import enum
import typing
import uuid

import pydantic

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,too-few-public-methods,missing-class-docstring,no-member,invalid-name

GameUuid = typing.NewType("GameUuid", uuid.UUID)
"""Game UUID"""

PlayerUuid = typing.NewType("PlayerUuid", uuid.UUID)
"""Player UUID"""

DealUuid = typing.NewType("DealUuid", uuid.UUID)
"""Deal UUID"""


class DealPhase(enum.Enum):
    """Phase of a bridge deal"""

    dealing = "dealing"
    bidding = "bidding"
    playing = "playing"
    ended = "ended"


class Position(enum.Enum):
    """Position of a bridge player"""

    north = "north"
    east = "east"
    south = "south"
    west = "west"


class Partnership(enum.Enum):
    """Partnership in a bridge game"""

    northSouth = "northSouth"
    eastWest = "eastWest"


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
    level: pydantic.conint(ge=1, le=7)

    class Config:
        schema_extra = {
            "example": {"strain": Strain.clubs, "level": 1},
        }


class Call(pydantic.BaseModel):
    """Call during bridge bidding phase

    A call is either a bid, pass, double or redouble. If (and only if)
    the call type is bid, must the bid property be populated.
    """

    type: CallType
    bid: typing.Optional[Bid]

    @pydantic.root_validator
    def _check_call_has_bid_iff_type_is_bid(cls, values):
        if bool(values.get("type") == CallType.bid) == bool(values.get("bid") is None):
            raise ValueError("Call must have bid if and only if its type is bid")
        return values

    class Config:
        schema_extra = {
            "example": {
                "type": CallType.bid,
                "bid": Bid(strain=Strain.hearts, level=4),
            },
        }


class Doubling(enum.Enum):
    """Doubling status of a bridge contract"""

    undoubled = "undoubled"
    doubled = "doubled"
    redoubled = "redoubled"


class Contract(pydantic.BaseModel):
    """Bridge contract"""

    bid: Bid
    doubling: Doubling

    class Config:
        schema_extra = {
            "example": {
                "bid": Bid(strain=Strain.hearts, level=4),
                "doubling": Doubling.undoubled,
            },
        }


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

    class Config:
        schema_extra = {
            "example": {"rank": Rank.ace, "suit": Suit.spades},
        }


CardList = typing.List[typing.Optional[CardType]]
"""List of cards, either revealed or not revealed"""


class CardsInHands(pydantic.BaseModel):
    """Cards in a bridge deal

    Cards held by the players in each position. A card may be either known or
    unknown, represented by a Card object or null, respectively.
    """

    north: CardList = []
    east: CardList = []
    south: CardList = []
    west: CardList = []

    class Config:
        schema_extra = {
            "example": {
                "north": [CardType(rank=Rank.queen, suit=Suit.hearts)],
                "east": [None],
                "south": [None],
                "west": [],
            },
        }


class Vulnerability(pydantic.BaseModel):
    """Vulnerability by partnership"""

    northSouth: bool = False
    eastWest: bool = False


class PositionCallPair(pydantic.BaseModel):
    """Position-call pair"""

    position: Position
    call: Call

    class Config:
        schema_extra = {
            "example": {"position": Position.north, "call": Call(type=CallType.pass_)},
        }


class PositionCardPair(pydantic.BaseModel):
    """Position-card pair"""

    position: Position
    card: CardType

    class Config:
        schema_extra = {
            "example": {
                "position": Position.north,
                "card": CardType(rank=Rank.seven, suit=Suit.diamonds),
            },
        }


class Trick(pydantic.BaseModel):
    """Trick in a bridge playing phase

    The cards array contains the cards played to the trick so far. A
    complete trick has four cards, one from each player. A complete
    trick also has a winner, which is the position that won the trick.

    The cards array may also be null for a trick that is closed.
    """

    cards: typing.Optional[typing.List[PositionCardPair]]
    winner: typing.Optional[Position]


class Deal(pydantic.BaseModel):
    """Bridge deal

    The deal object contains the description of an ongoing or
    completed deal. Depending on the phase of the deal, some or all of
    the data may be populated. Different information may be available
    to different players (notably which cards are visible to whom).
    """

    id: DealUuid = pydantic.Field(default_factory=uuid.uuid4)
    phase: DealPhase = DealPhase.dealing
    positionInTurn: typing.Optional[Position]
    calls: typing.List[PositionCallPair] = []
    declarer: typing.Optional[Position]
    contract: typing.Optional[Contract]
    cards: CardsInHands = CardsInHands()
    tricks: typing.List[Trick] = []
    vulnerability: Vulnerability = Vulnerability()


class PlayerState(pydantic.BaseModel):
    """Player state within a bridge deal

    The player state object doesn't describe the deal itself, but
    contains auxiliary information about the player and their choices
    in an ongoing deal.
    """

    position: typing.Optional[Position]
    allowedCalls: typing.List[Call] = []
    allowedCards: typing.List[CardType] = []

    class Config:
        schema_extra = {
            "example": {
                "position": Position.east,
                "allowedCalls": [],
                "allowedCards": [CardType(rank=Rank.ten, suit=Suit.clubs)],
            },
        }


class DuplicateResult(pydantic.BaseModel):
    """Duplicate bridge deal result

    A duplicate result consists of score and the partnership awarded that
    score. A passed out deal is represented by having null partnership and zero
    score.
    """

    partnership: typing.Optional[Partnership]
    score: pydantic.conint(ge=0) = 0

    class Config:
        schema_extra = {
            "example": {"partnership": Partnership.northSouth, "score": 100}
        }


class DealResult(pydantic.BaseModel):
    """Bridge game deal result

    A deal result consists of the deal, and a result object describing the
    outcome of that deal.
    """

    deal: DealUuid
    result: typing.Optional[DuplicateResult]


class PlayersInGame(pydantic.BaseModel):
    """Players in a bridge game

    Identifies the players sitting at each seat in a bridge game. Vacant seats
    are represented by null values.
    """

    north: typing.Optional[PlayerUuid]
    east: typing.Optional[PlayerUuid]
    south: typing.Optional[PlayerUuid]
    west: typing.Optional[PlayerUuid]


class Game(pydantic.BaseModel):
    """A bridge game"""

    id: GameUuid = pydantic.Field(default_factory=uuid.uuid4)
    deal: typing.Optional[Deal]
    self: PlayerState = PlayerState()
    results: typing.List[DealResult] = []
    players: PlayersInGame = PlayersInGame()
