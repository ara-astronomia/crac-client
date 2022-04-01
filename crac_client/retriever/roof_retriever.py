from multiprocessing import Queue
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
    def __init__(self, converter: Converter, queue: Queue) -> None:
        super().__init__(converter, queue)

    def setAction(self, action: str):
        request = RoofRequest(action=RoofAction.Value(action))
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = RoofStub(channel)
            response = client.SetAction(request, wait_for_ready=True)
            self.callback(response)
