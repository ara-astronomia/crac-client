from datetime import datetime
import logging
from crac_client.config import Config
from crac_client.retriever.retriever import Retriever
from crac_protobuf.ups_pb2 import (
    UpsRequest,
    UpsResponse,
)
from crac_protobuf.ups_pb2_grpc import (
    UpsStub,
)
import grpc


logger = logging.getLogger(__name__)


class UpsRetriever(Retriever):
    def __init__(self, converter) -> None:
        super().__init__(converter)
        self.channel = grpc.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = UpsStub(self.channel)

    def getStatus(self, latest_update: str, interval: str) -> UpsResponse:
        logging.debug(f"latest update is {latest_update}")
        logging.debug(f"interval is {interval}")
        call_future = self.client.GetStatus.future(UpsRequest())
        call_future.add_done_callback(self.callback)
