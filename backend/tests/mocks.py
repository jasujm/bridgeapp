"""Mock classes to be used in unit tests"""

import contextlib
import typing

import zmq
import zmq.utils.z85 as z85

from bridgeapp import bridgeprotocol


class MockBridgeServer(contextlib.AbstractContextManager):
    """Introspectable mock bridge server for unit tests

    It has the following limitations:

    - Only one server can exist per ZeroMQ context.
    - It must receive messages from a single client.
    """

    def __init__(
        self, ctx: zmq.asyncio.Context, tmpdir, secretkey: typing.Optional[bytes] = None
    ):
        """
        Parameters:
            ctx: The ZeroMQ context
            tmpdir: Temporary directory where the sockets are created
            secretkey: CURVE secret key
        """
        self._mock_server_endpoint = f"ipc://{tmpdir.join('server.endpoint')}"
        self._socket = ctx.socket(zmq.ROUTER)
        if secretkey:
            self._socket.curve_server = 1
            self._socket.curve_secretkey = z85.decode(secretkey)
        self._socket.bind(self._mock_server_endpoint)
        self._router_id = None
        self._mock_event_endpoint = f"ipc://{tmpdir.join('event.endpoint')}"
        self._event_socket = ctx.socket(zmq.PUB)
        if secretkey:
            self._event_socket.curve_server = 1
            self._event_socket.curve_secretkey = z85.decode(secretkey)
        self._event_socket.bind(self._mock_event_endpoint)

    def close(self):
        """Close the underlying sockets"""
        self._socket.close()
        self._event_socket.close()

    def __exit__(self, *args):
        self.close()

    async def get_command(
        self,
    ) -> typing.Tuple[bytes, bytes, typing.Dict[bytes, bytes]]:
        """Retrieve and return the latest command sent to the server

        Returns:
            A tuple containing the tag, the command and the command
            arguments, respectively
        """
        (
            router_id,
            _,
            tag,
            command,
            *command_arguments,
        ) = await self._socket.recv_multipart()
        assert self._router_id is None or self._router_id == router_id
        self._router_id = router_id
        assert len(command_arguments) % 2 == 0
        return tag, command, bridgeprotocol.utils.group_arguments(command_arguments)

    async def reply(
        self, tag: bytes, status: bytes, reply_arguments: typing.Mapping[bytes, bytes]
    ):
        await self.send(
            tag, status, *bridgeprotocol.utils.flatten_arguments(reply_arguments)
        )

    async def send(self, *frames: bytes):
        msg = [self._router_id, b"", *frames]
        await self._socket.send_multipart(msg)

    async def send_event(
        self, tag: bytes, event_arguments: typing.Mapping[bytes, bytes]
    ):
        await self._event_socket.send_multipart(
            [tag, *bridgeprotocol.utils.flatten_arguments(event_arguments)]
        )

    @property
    def endpoint(self) -> str:
        """The endpoint the server binds to"""
        return self._mock_server_endpoint

    @property
    def event_endpoint(self) -> str:
        """The endpoint the server binds to"""
        return self._mock_event_endpoint
