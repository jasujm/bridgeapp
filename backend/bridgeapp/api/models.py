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
    base_models.GameUuid: _UuidConversion(handler="game_details", uuidarg="game_uuid",),
    base_models.PlayerUuid: _UuidConversion(
        handler="player_details", uuidarg="player_uuid"
    ),
    base_models.DealUuid: _UuidConversion(handler="deal_details", uuidarg="deal_uuid"),
}


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
        values[name] = value
    return cls(**values)


def _apify_field(field: pydantic.fields.ModelField):
    new_type = (
        field.type_
        if field.outer_type_ not in _UUID_TO_URL_CONVERSION
        else pydantic.AnyHttpUrl
    )
    if not field.required:
        new_type = typing.Optional[new_type]
    return (new_type, field.default)


def _apify_model(
    model: typing.Type[pydantic.BaseModel],
) -> typing.Type[pydantic.BaseModel]:
    new_fields = {
        name: _apify_field(field) for (name, field) in model.__fields__.items()
    }
    new_model = pydantic.create_model(model.__name__, __base__=model, **new_fields)
    new_model.from_base_model = classmethod(_from_base_model)
    return new_model


class Game(base_models.Game):
    """Bridge game

    Mode lpcontaining the basic information of a game, and the current
    deal state.
    """

    deal: typing.Optional[base_models.Deal]


class Player(base_models.IdentifiableModel):
    """Player taking part in a bridge game"""


PlayersInGame = _apify_model(base_models.PlayersInGame)
DealResult = _apify_model(base_models.DealResult)
BridgeEvent = _apify_model(base_events.BridgeEvent)


class Error(pydantic.BaseModel):
    """Error details"""

    detail: str
