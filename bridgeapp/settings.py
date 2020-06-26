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

    api_v1_prefix = Field("/api/v1", title="The API URL prefix")

    backend_endpoint: str = Field(
        "tcp://localhost:5555",
        title="Bridge backend server endpoint",
        regex=TCP_ENDPOINT_RE,
    )

    uuid_namespace: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        title="Root namespace for UUIDs",
        description="""
The application uses UUIDv5 algorithm to generate UUIDs e.g. for players based
on their username. This setting is used as the root namespace. It should be set
to a known value to ensure consistent UUID generation across runs."""
    )

    class Config:  # pylint: disable=missing-class-docstring
        env_prefix = "bridgeapp_"


@functools.lru_cache
def get_settings(**kwargs) -> Settings:
    """Get the application settings

    Parameters:
        kwargs: The settings to be overridden
    """
    return Settings(**kwargs)
