"""
Models consumed and produced by the API
---------------------------------------

The models in this module extend the base models.
"""

from bridgeapp import models as base_models


class Game(base_models.Game):
    """Bridge game

    Model containing the basic information of a game, and the current
    deal state.
    """

    deal = base_models.DealState()
