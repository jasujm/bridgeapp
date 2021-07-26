"""
Models consumed and produced by the API
.......................................

The models in this module extend the base models.
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use,too-few-public-methods,missing-class-docstring,no-member

import typing

import fastapi
import pydantic

from bridgeapp.bridgeprotocol import models as base_models, events as base_events

# Some funky Python magic for creating models that automagically
# convert UUID fields of source models into API URLs. Botched together
# with limited knowledge about pydantic and if it could have been done
# more elegantly.

GameUrl = typing.NewType("GameUrl", pydantic.AnyHttpUrl)
"""Game URL"""

PlayerUrl = typing.NewType("PlayerUrl", pydantic.AnyHttpUrl)
"""Player URL"""

DealUrl = typing.NewType("DealUrl", pydantic.AnyHttpUrl)
"""Deal URL"""

_UUID_TO_URL_MAP = {
    base_models.GameUuid: GameUrl,
    base_models.PlayerUuid: PlayerUrl,
    base_models.DealUuid: DealUrl,
}


def _get_uuid_converter(handler: str, id_kwarg_name: str):
    # pylint: disable=redefined-builtin
    def _uuid_converter(request: fastapi.Request, id: str):
        return request.url_for(handler, **{id_kwarg_name: id})

    return _uuid_converter


_URL_CONVERTERS = {
    GameUrl: _get_uuid_converter("game_details", "game_id"),
    PlayerUrl: _get_uuid_converter("player_details", "player_id"),
    DealUrl: _get_uuid_converter("deal_details", "deal_id"),
}


def _from_attributes(
    cls,
    attrs: typing.Iterable[typing.Tuple[str, typing.Any]],
    request: typing.Union[fastapi.Request, fastapi.WebSocket],
):
    values = {}
    source_fields = getattr(attrs, "__fields__", {})
    obj_id = None
    for (name, value) in attrs:
        if name == "id":
            obj_id = value
        if field := (cls.__fields__.get(name, None) or source_fields.get(name, None)):
            if value and (url_converter := (_URL_CONVERTERS.get(field.outer_type_))):
                value = url_converter(request, value)
        values[name] = value
    if (
        obj_id
        and (field := cls.__fields__.get("self"))
        and (url_converter := _URL_CONVERTERS.get(field.outer_type_))
    ):
        values["self"] = url_converter(request, obj_id)
    return cls(**values)


def _apify_field_type(outer_type_):
    if typing.get_origin(outer_type_) == typing.Union:
        return typing.Union[
            tuple(_apify_field_type(t) for t in typing.get_args(outer_type_))
        ]
    if url_type := _UUID_TO_URL_MAP.get(outer_type_):
        return url_type
    return outer_type_


def _apify_field(field: pydantic.fields.ModelField):
    return (_apify_field_type(field.outer_type_), field.default)


def _apify_model(
    model: typing.Type[pydantic.BaseModel],
) -> typing.Type[pydantic.BaseModel]:
    # ID fields of foreign objects are converted to URLs instead of UUIDs. The
    # sole exception is the field called `id` which refers to the ID of the
    # model itself. But add an additional `self` field which is the URL of the
    # instance.
    new_fields = {
        name: _apify_field(field)
        if name != "id"
        else (field.outer_type_, field.default)
        for (name, field) in model.__fields__.items()
    }
    if id_field := model.__fields__.get("id"):
        new_fields["self"] = _apify_field(id_field)
    new_model = pydantic.create_model(
        model.__name__, __config__=model.__config__, **new_fields
    )
    new_model.__doc__ = model.__doc__
    new_model.from_attributes = classmethod(_from_attributes)
    return new_model


Deal = _apify_model(base_models.Deal)


Username = pydantic.constr(min_length=2, max_length=31, regex=r"^[\s\w\d_ -]{1,31}$")
"""Username string"""


class _PlayerBase(pydantic.BaseModel):
    username: Username


@_apify_model
class Player(_PlayerBase):
    """Player taking part in a bridge game"""

    id: base_models.PlayerUuid


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


DealResult = _apify_model(base_models.DealResult)
BridgeEvent = _apify_model(base_events.BridgeEvent)


class _GameBase(pydantic.BaseModel):
    name: pydantic.constr(min_length=2, max_length=63)


@_apify_model
class GameSummary(_GameBase):
    """Bridge game summary

    Contains static information about a game, excluding any game state.
    """

    id: base_models.GameUuid
    isPublic: bool
    players: PlayersInGame = PlayersInGame()


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


class Error(pydantic.BaseModel):
    """Error details"""

    detail: str
