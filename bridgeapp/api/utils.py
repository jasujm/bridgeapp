"""
Bridgeapp API utilities
-----------------------
"""

import uuid

from bridgeapp import settings

PLAYER_UUID_NS = uuid.uuid5(settings.get_settings().uuid_namespace, "players")
"""UUID namespace for bridge players"""


def generate_player_uuid(username: str) -> uuid.UUID:
    """Generate UUID for a player from ``username``"""
    return uuid.uuid5(PLAYER_UUID_NS, username)