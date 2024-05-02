import grpc
import sys
import logging
import logging.config
from concurrent import futures

import auth_pb2_grpc
from config import settings
from config.di import Container
from grpc_services.auth import GRPCAuth
from utils.logging import get_config


formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO if settings.DEBUG else logging.CRITICAL)
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if settings.DEBUG else logging.CRITICAL)
logger.addHandler(handler)


class GRPCServer:
    def run(self) -> None:
        logger.info("Auth GRPC Start Up...")
        self._init_di()
        logger.info("DI Container Successfully Initialized...")
        self._init_logging()
        logger.info("Logging Successfully Initialized...")
        server = self._create_server()
        logger.info("gRPC Server Successfully Created...")
        self._add_services(server)
        logger.info("Successfully Added gRPC Services to the Server...")
        self._init_port(server)
        logger.info("Server Port Successfully Initialized...")
        self._start_server(server)
        logger.info(f"Running at {self._get_address()}")
        self._wait_for_termination(server)

    def _init_di(self) -> None:
        Container()

    def _init_logging(self) -> None:
        logging.config.dictConfig(get_config(settings.LOG_PATH))

    def _create_server(self) -> grpc.aio.Server:
        return grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    def _add_services(self, server: grpc.aio.Server) -> None:
        auth_pb2_grpc.add_AuthServicer_to_server(GRPCAuth(), server)

    def _get_address(self) -> str:
        return f"{settings.AUTH_GRPC_SERVER_HOST}:{settings.AUTH_GRPC_SERVER_PORT}"

    def _init_port(self, server: grpc.aio.Server) -> None:
        server.add_insecure_port(self._get_address())

    def _start_server(self, server: grpc.aio.Server) -> None:
        server.start()

    def _wait_for_termination(self, server: grpc.aio.Server) -> None:
        server.wait_for_termination()


if __name__ == "__main__":
    GRPCServer().run()
