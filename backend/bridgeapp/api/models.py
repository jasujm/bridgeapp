"""
Models consumed and produced by the API
.......................................

The models in this module extend the base models.
"""

# Docstrings and methods come from parent in this case
# pylint: disable=missing-class-docstring,too-few-public-methods

import typing
import uuid

import fastapi
import hrefs
import hrefs.starlette
import pydantic

from bridgeapp.bridgeprotocol import models as base_models, events as base_events


def _get_uuid_converter(handler: str):
    def _uuid_converter(ws: fastapi.WebSocket, id: str):
        return ws.url_for(handler, id=id)

    return _uuid_converter


_URL_CONVERTERS = {
    base_models.GameUuid: _get_uuid_converter("game_details"),
    base_models.PlayerUuid: _get_uuid_converter("player_details"),
    base_models.DealUuid: _get_uuid_converter("deal_details"),
}


def _get_url_converter(field_type: typing.Type):
    if typing.get_origin(field_type) is typing.Union:
        for type_arg in typing.get_args(field_type):
            if url_converter := _get_url_converter(type_arg):
                return url_converter
    return _URL_CONVERTERS.get(field_type)


def _populate_self_validator():
    def _populate_self(cls, values):
        del cls
        if values.get("self", None) is None:
            values["self"] = values["id"]
        return values

    return pydantic.root_validator(pre=True, allow_reuse=True)(_populate_self)


class Deal(base_models.Deal, hrefs.starlette.ReferrableModel):
    id: uuid.UUID
    self: hrefs.Href["Deal"]

    populate_self = _populate_self_validator()

    class Config:
        details_view = "deal_details"


Username = pydantic.constr(min_length=2, max_length=31, regex=r"^[\s\w\d_ -]{1,31}$")
"""Username string"""


class _PlayerBase(pydantic.BaseModel):
    username: Username


class Player(_PlayerBase, hrefs.starlette.ReferrableModel):
    """Player taking part in a bridge game"""

    id: uuid.UUID
    self: hrefs.Href["Player"]

    populate_self = _populate_self_validator()

    class Config:
        details_view = "player_details"


class PlayerCreate(_PlayerBase):
    """Model for creating a player"""

    password: pydantic.SecretStr


class PlayerUpdate(pydantic.BaseModel):
    """Model for updating a player"""

    password: typing.Optional[pydantic.SecretStr]


class PlayersInGame(pydantic.BaseModel):
    north: typing.Optional[Player]
    east: typing.Optional[Player]
    south: typing.Optional[Player]
    west: typing.Optional[Player]


class DealResult(base_models.DealResult):
    deal: hrefs.Href[Deal]


class _GameBase(pydantic.BaseModel):
    name: pydantic.constr(min_length=2, max_length=63)


class GameSummary(_GameBase, hrefs.starlette.ReferrableModel):
    """Bridge game summary

    Contains static information about a game, excluding any game state.
    """

    id: uuid.UUID
    self: hrefs.Href["Game"]
    isPublic: bool = True
    players: PlayersInGame = PlayersInGame()

    populate_self = _populate_self_validator()

    class Config:
        details_view = "game_details"


# pylint: disable=too-many-ancestors
class Game(GameSummary):
    """Bridge game

    Model containing the full description of the state of a game, from the point
    of view of a player.
    """

    deal: typing.Optional[Deal]
    me: base_models.PlayerState = base_models.PlayerState()
    results: typing.List[DealResult] = []


class GameCreate(_GameBase):
    """Model for creating a bridge game"""

    isPublic: bool = True


class BridgeEvent(base_events.BridgeEvent):
    game: pydantic.AnyHttpUrl

    @classmethod
    def from_base(
        cls, base_model: base_events.BridgeEvent, ws: fastapi.WebSocket,
    ):
        """Create API :class:`BridgeEvent` from :class:`bridgeapp.bridgeprotocol.BridgeEvent`

        It converts all UUIDs in the base model into API URLs, otherwise keeps
        the fields the same.

        Arguments:
            base_model: the base event instance
            ws: the websocket object

        Returns:
            An instance with all UUIDs from the base model replaced with URLs
        """
        values = {}
        source_fields = base_model.__fields__
        for (name, value) in base_model:
            if field := (
                source_fields.get(name, None) or cls.__fields__.get(name, None)
            ):
                if value and (url_converter := _get_url_converter(field.outer_type_)):
                    value = url_converter(ws, value)
            values[name] = value
        return cls(**values)


class Error(pydantic.BaseModel):
    """Error details"""

    detail: str


Deal.update_forward_refs()
Player.update_forward_refs()
DealResult.update_forward_refs()
GameSummary.update_forward_refs()
Game.update_forward_refs()
