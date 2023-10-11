from crac_client.config import Config
from crac_client.converter.converter import Converter
from crac_client.retriever.retriever import Retriever
from crac_protobuf.roof_pb2 import (
    RoofAction,
    RoofRequest
)
from crac_protobuf.roof_pb2_grpc import (
    RoofStub,
)
import grpc


class RoofRetriever(Retriever):
    def __init__(self, converter: Converter) -> None:
        super().__init__(converter)
        self.channel = grpc.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = RoofStub(self.channel)

    async def setAction(self, action: str):
        request = RoofRequest(action=RoofAction.Value(action))
        call_future = self.client.SetAction.future(request, wait_for_ready=True)
        call_future.add_done_callback(self.callback)
