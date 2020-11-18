"""
Exceptions
,,,,,,,,,,
"""

import typing


class ProtocolError(Exception):
    """Generic protocol error"""


class InvalidMessage(ProtocolError):
    """Error signaling invalid message received from the server"""


class CommandFailure(ProtocolError):
    """Error signaling failed command"""

    def __init__(self, message=None, code=None):
        super().__init__(message)
        self._code: typing.Optional[str] = code

    @property
    def code(self) -> typing.Optional[str]:
        return self._code
