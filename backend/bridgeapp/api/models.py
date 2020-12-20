"""
Models consumed and produced by the API
.......................................

The models in this module extend the base models.
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use,too-few-public-methods,missing-class-docstring,no-member

from collections import namedtuple
import typing

import fastapi
import pydantic

from bridgeapp.bridgeprotocol import models as base_models, events as base_events

# Some funky Python magic for creating models which automagically convert UUID
# fields of the base models into API URLs. Botched together with limited
# knowledge about pydantic and if it could have been done more elegantly.

_UuidConversion = namedtuple("_UuidConversion", "handler uuidarg")

_UUID_TO_URL_CONVERSION = {
    base_models.GameUuid: _UuidConversion(handler="game_details", uuidarg="game_id",),
    base_models.PlayerUuid: _UuidConversion(
        handler="player_details", uuidarg="player_id"
    ),
    base_models.DealUuid: _UuidConversion(handler="deal_details", uuidarg="deal_id"),
}


def _apify_field_name(name: str):
    if name == "id":
        return "self"
    return name


def _from_base_model(
    cls,
    model: pydantic.BaseModel,
    request: typing.Union[fastapi.Request, fastapi.WebSocket],
):
    values = {}
    for (name, field) in model.__fields__.items():
        value = getattr(model, name, field.default)
        if value and (conversion := (_UUID_TO_URL_CONVERSION.get(field.outer_type_))):
            kwargs = {conversion.uuidarg: value}
            value = request.url_for(conversion.handler, **kwargs)
        values[_apify_field_name(name)] = value
    return cls(**values)


def _apify_field_type(outer_type_):
    if typing.get_origin(outer_type_) == typing.Union:
        return typing.Union[
            tuple(_apify_field_type(t) for t in typing.get_args(outer_type_))
        ]
    if outer_type_ in _UUID_TO_URL_CONVERSION:
        return pydantic.AnyHttpUrl
    return outer_type_


def _apify_field(field: pydantic.fields.ModelField):
    return (_apify_field_type(field.outer_type_), field.default)


def _apify_model(
    model: typing.Type[pydantic.BaseModel],
) -> typing.Type[pydantic.BaseModel]:
    # Rename id -> self, otherwise take the name as is
    # In the API response we prefer URLs to raw UUID
    new_fields = {
        _apify_field_name(name): _apify_field(field)
        for (name, field) in model.__fields__.items()
    }
    new_model = pydantic.create_model(
        model.__name__, __config__=model.__config__, **new_fields
    )
    new_model.__doc__ = model.__doc__
    new_model.from_base_model = classmethod(_from_base_model)
    return new_model


Deal = _apify_model(base_models.Deal)


class Player(pydantic.BaseModel):
    """Player taking part in a bridge game"""

    self: pydantic.AnyHttpUrl


PlayersInGame = _apify_model(base_models.PlayersInGame)
DealResult = _apify_model(base_models.DealResult)
BridgeEvent = _apify_model(base_events.BridgeEvent)


class Game(pydantic.BaseModel):
    """Bridge game

    Model containing the full description of the state of a game, from the point
    of view of a player.
    """

    self: pydantic.AnyHttpUrl
    deal: typing.Optional[Deal]
    me: base_models.PlayerState = base_models.PlayerState()
    results: typing.List[DealResult] = []
    players: PlayersInGame = PlayersInGame()


class Error(pydantic.BaseModel):
    """Error details"""

    detail: str
