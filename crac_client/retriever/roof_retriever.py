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
        self.channel = grpc.aio.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = RoofStub(self.channel)

    async def setAction(self, action: str):
        request = RoofRequest(action=RoofAction.Value(action))
        response = await self.client.SetAction(request, wait_for_ready=True)
        self.converter.convert(response)
