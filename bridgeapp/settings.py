"""
Bridgeapp settings
------------------
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use,too-few-public-methods


import functools
import uuid

from pydantic import BaseSettings, Field

from .bridgeprotocol.utils import TCP_ENDPOINT_RE


class Settings(BaseSettings):
    """Bridgeapp settings"""

    backend_endpoint: str = Field("tcp://localhost:5555", regex=TCP_ENDPOINT_RE)
    """Bridge backend server endpoint"""

    uuid_namespace: uuid.UUID = Field(default_factory=uuid.uuid4)
    """Root namespace for UUIDs

    The application uses UUIDv5 algorithm to generate UUIDs e.g. for
    players based on their username. This setting is used as the root
    namespace. It should be set to a known value to ensure consistent
    UUID generation across runs.
    """

    class Config:  # pylint: disable=missing-class-docstring
        env_prefix = "bridgeapp_"


@functools.lru_cache
def get_settings(**kwargs):
    """Get the application settings

    Parameters:
        kwargs: The settings to be overridden
    """
    return Settings(**kwargs)
