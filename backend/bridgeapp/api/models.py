"""
Models consumed and produced by the API
.......................................

The models in this module extend the base models.
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use,too-few-public-methods,missing-class-docstring,no-member


import typing

from bridgeapp import models as base_models


class Game(base_models.Game):
    """Bridge game

    Model containing the basic information of a game, and the current
    deal state.
    """

    deal: typing.Optional[base_models.Deal]
