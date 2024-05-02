from typing import TypeVar, Generic

import grpc


T = TypeVar("T")


class GRPCConnection(Generic[T]):
    """Class responsible for initializing grpc channel at startup"""

    def __init__(self, host: str, port: int, stub: T):
        """Init a channel"""
        self.channel = grpc.aio.insecure_channel(f"{host}:{port}")
        self._stub = stub(self.channel)

    @property
    def stub(self) -> T:
        """Get a stub to use for the grpc"""
        return self._stub
