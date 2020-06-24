"""
Bridgeapp API utilities
-----------------------
"""

import uuid

from bridgeapp import settings

player_uuid_ns = uuid.uuid5(settings.get_settings().uuid_namespace, "players")


def generate_player_uuid(username: str) -> uuid.UUID:
    """Generate UUID for a player from ``username``"""
    return uuid.uuid5(player_uuid_ns, username)
