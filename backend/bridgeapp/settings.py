"""
Bridgeapp settings
------------------
"""

# Don't care about warning related to pydantic conventions
# pylint: disable=no-self-argument,no-self-use,too-few-public-methods


import functools
import typing
import uuid

from pydantic import BaseSettings, Field, root_validator

from .bridgeprotocol.utils import TCP_ENDPOINT_RE
from .bridgeprotocol import CurveKeys


class Settings(BaseSettings):
    """Bridgeapp settings"""

    api_v1_prefix = Field("/api/v1", title="The API URL prefix")

    backend_endpoint: str = Field(
        "tcp://localhost:5555",
        title="Bridge backend server endpoint",
        regex=TCP_ENDPOINT_RE.pattern,
    )

    backend_event_endpoint: str = Field(
        "tcp://localhost:5556",
        title="Bridge backend event endpoint",
        regex=TCP_ENDPOINT_RE.pattern,
    )

    curve_serverkey: typing.Optional[str] = Field(
        title="Bridge backend server key",
        description="""
The public key of the bridge backend server. If this is set together with the
client keys, use ZeroMQ CURVE mechanism to connect securely with the bridge
backend."""
    )

    curve_publickey: typing.Optional[str] = Field(
        title="Bridge client public key",
        description="""
The public key of the bridge client. If this is set together with the client
keys, use ZeroMQ CURVE mechanism to connect securely with the bridge backend.
"""
    )

    curve_secretkey: typing.Optional[str] = Field(
        title="Bridge client secret key",
        description="""
The secret key of the bridge client. If this is set together with the client
keys, use ZeroMQ CURVE mechanism to connect securely with the bridge backend.
"""
    )

    uuid_namespace: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        title="Root namespace for UUIDs",
        description="""
The application uses UUIDv5 algorithm to generate UUIDs e.g. for players based
on their username. This setting is used as the root namespace. It should be set
to a known value to ensure consistent UUID generation across runs.""",
    )

    @property
    def curve_keys(self) -> CurveKeys:
        """Return curve keys from the settings"""
        return CurveKeys(
            serverkey=self.curve_serverkey,
            publickey=self.curve_publickey,
            secretkey=self.curve_secretkey,
        )

    @root_validator
    def _check_curve_keys(cls, values):
        keys = [values.get(k) for k in ("curve_serverkey", "curve_publickey", "curve_secretkey")]
        if not all(key is None for key in keys) and not all(key is not None for key in keys):
            raise ValueError("Either all or none of the curve keys must be defined")
        return values

    class Config:  # pylint: disable=missing-class-docstring
        env_prefix = "bridgeapp_"


@functools.lru_cache
def get_settings(**kwargs) -> Settings:
    """Get the application settings

    Parameters:
        kwargs: The settings to be overridden
    """
    return Settings(**kwargs)


settings = Settings()
