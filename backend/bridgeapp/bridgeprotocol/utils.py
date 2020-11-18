"""
Utilities
,,,,,,,,,
"""

import collections.abc as cabc
import re

import more_itertools as mi

TCP_ENDPOINT_RE = re.compile(r"^tcp://(.+):(\d+)$")
"""Regular expression matching ZeroMQ TCP endpoint"""

ERROR_STATUS_RE = re.compile(r"^ERR:(.*)$")


def endpoints(control_endpoint: str):
    """Get a tuple containing control and event endpoints to a server

    Given a control endpoint, returns a tuple containing the control
    and event endpoints to a bridge server. The endpoints are TCP
    connections at successive ports, for example:

    .. testsetup::

        from bridgeapp.bridgeprotocol.utils import endpoints

    .. doctest::

        >>> endpoints("tcp://localhost:5555")
        ('tcp://localhost:5555', 'tcp://localhost:5556')

    Parameters:
        control_endpoint: The control endpoint of the bridge backend

    Raises:
        :exc:`ValueError`: If ``control_endpoint`` is not a correctly
          formatted TCP endpoint
    """
    if m := TCP_ENDPOINT_RE.fullmatch(control_endpoint):
        address, control_port = m.groups()
        event_port = int(control_port) + 1
        return control_endpoint, f"tcp://{address}:{event_port}"
    raise ValueError(f"Expected TCP endpoint, got: {control_endpoint}")


def merge_patch(target: cabc.MutableMapping, patch):
    """Apply JSON merge patch to target

    This function is implementation of the JSON Merget Patch algorithm
    described in RFC 7396. ``target`` is patched in place.

    Parameters:
        target: The target object
        patch: The patch to apply

    Return:
        The result of applying the patch. The returned object may or
        may not be the ``target`` parameter.
    """
    if isinstance(patch, cabc.Mapping):
        if not isinstance(target, cabc.Mapping):
            target = {}
        for key in list(patch.keys()):
            if (value := patch[key]) is None:
                target.pop(key, None)
            else:
                target[key] = merge_patch(target.get(key, {}), value)
        return target
    return patch


def group_arguments(args):
    """Group flat key-value pairs into dictionary"""
    return dict(mi.grouper(args, 2))


def flatten_arguments(args):
    """Flatten dictionary into key-value pairs"""
    return mi.flatten(args.items())


def is_status_successful(status: bytes):
    """Determine if a status frame indicates successful reply"""
    return status.startswith(b"OK")


def get_error_code(status: bytes):
    """Return error code in a status frame"""
    m = ERROR_STATUS_RE.match(status.decode())
    return m and m.group(1)
