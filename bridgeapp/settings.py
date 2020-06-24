"""
Bridgeapp settings
------------------
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use,too-few-public-methods


import functools

from pydantic import BaseSettings, Field

from .bridgeprotocol.utils import TCP_ENDPOINT_RE


class Settings(BaseSettings):
    """Bridgeapp settings"""

    backend_endpoint: str = Field("tcp://localhost:5555", regex=TCP_ENDPOINT_RE)
    """Bridge backend server endpoint"""

    class Config:  # pylint: disable=missing-class-docstring
        env_prefix = "bridgeapp_"


@functools.lru_cache
def get_settings(**kwargs):
    """Get the application settings

    Parameters:
        kwargs: The settings to be overridden
    """
    return Settings(**kwargs)
