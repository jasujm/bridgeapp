"""
Models consumed and produced by the API
---------------------------------------

The models in this module extend the base models.
"""

from bridgeapp import models as base_models


class Game(base_models.Game):
    """Game representation in the API"""

    deal = base_models.DealState()
