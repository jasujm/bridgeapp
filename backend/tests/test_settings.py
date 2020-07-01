"""
Tests for the :mod:`bridgeapp.settings` module
"""

import pytest

import pydantic

from bridgeapp import settings


@pytest.mark.parametrize(
    "backend_endpoint", ["tcp://localhost:5555", "tcp://example.com:1234"]
)
def test_backend_endpoint(backend_endpoint):
    s = settings.get_settings(backend_endpoint=backend_endpoint)
    assert s.backend_endpoint == backend_endpoint


@pytest.mark.parametrize(
    "backend_endpoint", ["inproc://wrong.endpoint", "tcp://localhost:not-a-port"]
)
def test_endpoints_should_fail_if_control_endpoint_has_wrong_format(backend_endpoint):
    with pytest.raises(pydantic.ValidationError):
        settings.get_settings(backend_endpoint=backend_endpoint)
