"""
Exceptions
,,,,,,,,,,
"""


class ProtocolError(Exception):
    """Generic protocol error"""


class InvalidMessage(ProtocolError):
    """Error indicating invalid message received from the server"""


class CommandFailure(ProtocolError):
    """Error indicating failed command"""


class UnknownClientError(CommandFailure):
    """Error indicating failure due to missing handshake"""


class NotFoundError(CommandFailure):
    """Error indicating game not found"""


class AlreadyExistsError(CommandFailure):
    """Error indicating a game couldn't be created because it already exists"""


class NotAuthorizedError(CommandFailure):
    """Error indicating an action wasn't authorized"""


class SeatReservedError(CommandFailure):
    """Error indicating joining a game failed due to seat being reserved"""


class RuleViolationError(CommandFailure):
    """Error indicating action being against the rules of contract bridge"""
