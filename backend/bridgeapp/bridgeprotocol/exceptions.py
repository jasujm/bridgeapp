"""
Exceptions
,,,,,,,,,,
"""


class ProtocolError(Exception):
    """Generic protocol error"""


class InvalidMessage(ProtocolError):
    """Error signaling invalid message received from the server"""


class CommandFailure(ProtocolError):
    """Error signaling failed command"""
