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

# Some funky Python magic for creating models which automagically convert UUID
# fields of the base models into API URLs. Botched together with limited
# knowledge about pydantic and if it could have been done more elegantly.


def _get_uuid_converter(handler: str, id_kwarg_name: str):
    # pylint: disable=redefined-builtin
    def _uuid_converter(request: fastapi.Request, id: str):
        return request.url_for(handler, **{id_kwarg_name: id})

    return _uuid_converter


_UUID_TO_URL_CONVERTERS = {
    base_models.GameUuid: _get_uuid_converter("game_details", "game_id"),
    base_models.PlayerUuid: _get_uuid_converter("player_details", "player_id"),
    base_models.DealUuid: _get_uuid_converter("deal_details", "deal_id"),
}


def _from_base_model(
    cls,
    model: pydantic.BaseModel,
    request: typing.Union[fastapi.Request, fastapi.WebSocket],
):
    values = {}
    for (name, field) in model.__fields__.items():
        value = getattr(model, name, field.default)
        if value and (
            url_converter := (_UUID_TO_URL_CONVERTERS.get(field.outer_type_))
        ):
            if name == "id":
                values["self"] = url_converter(request, value)
            else:
                value = url_converter(request, value)
        values[name] = value
    return cls(**values)


def _apify_field_type(outer_type_):
    if typing.get_origin(outer_type_) == typing.Union:
        return typing.Union[
            tuple(_apify_field_type(t) for t in typing.get_args(outer_type_))
        ]
    if outer_type_ in _UUID_TO_URL_CONVERTERS:
        return pydantic.AnyHttpUrl
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
    new_model.from_base_model = classmethod(_from_base_model)
    return new_model


Deal = _apify_model(base_models.Deal)


Username = pydantic.constr(min_length=2, max_length=31, regex=r"^[\s\w\d_ -]{1,31}$")
"""Username string"""


class _PlayerBase(pydantic.BaseModel):
    username: Username


class Player(_PlayerBase):
    """Player taking part in a bridge game"""

    id: base_models.PlayerUuid
    self: pydantic.AnyHttpUrl


class PlayerCreate(_PlayerBase):
    """Model for creating a player"""

    password: pydantic.SecretStr


PlayersInGame = _apify_model(base_models.PlayersInGame)
DealResult = _apify_model(base_models.DealResult)
BridgeEvent = _apify_model(base_events.BridgeEvent)


class Game(pydantic.BaseModel):
    """Bridge game

    Model containing the full description of the state of a game, from the point
    of view of a player.
    """

    id: base_models.GameUuid
    self: pydantic.AnyHttpUrl
    deal: typing.Optional[Deal]
    me: base_models.PlayerState = base_models.PlayerState()
    results: typing.List[DealResult] = []
    players: PlayersInGame = PlayersInGame()


class Error(pydantic.BaseModel):
    """Error details"""

    detail: str
