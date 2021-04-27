"""
ElasticSearch definitions
.........................

This module contains setup for the ElasticSearch client and document
models.
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=too-few-public-methods

import logging

import elasticsearch_dsl

from bridgeapp.settings import settings

logger = logging.getLogger(__name__)

elasticsearch_dsl.connections.create_connection(hosts=[settings.elasticsearch_host])


class Player(elasticsearch_dsl.InnerDoc):
    """Player search model"""

    id = elasticsearch_dsl.Text()
    username = elasticsearch_dsl.Text()


class PlayersInGame(elasticsearch_dsl.InnerDoc):
    """Players in game search model"""

    north = elasticsearch_dsl.Object(Player)
    east = elasticsearch_dsl.Object(Player)
    south = elasticsearch_dsl.Object(Player)
    west = elasticsearch_dsl.Object(Player)


class GameSummary(elasticsearch_dsl.Document):
    """Game search model"""

    id = elasticsearch_dsl.Text()
    name = elasticsearch_dsl.Text()
    players = elasticsearch_dsl.Object(PlayersInGame)

    class Index:  # pylint: disable=missing-class-docstring
        name = "games"


def init():
    """Initializes search indices"""
    GameSummary.init()
    logger.info("Search indices created")
