from queue import Queue
from crac_client.config import Config
from crac_client.converter.converter import Converter
from crac_client.retriever.retriever import Retriever
from crac_protobuf.curtains_pb2 import (
    CurtainsAction,
    CurtainsRequest,
)
from crac_protobuf.curtains_pb2_grpc import CurtainStub
from crac_protobuf.button_pb2 import (
    ButtonKey,
)
import grpc


class CurtainsRetriever(Retriever):
    def __init__(self, converter: Converter, queue: Queue) -> None:
        super().__init__(converter, queue)

    key_to_curtains_action_conversion = [
        ButtonKey.KEY_CURTAINS,
        ButtonKey.KEY_CALIBRATE,
    ]

    def setAction(self, action: str):
        request = CurtainsRequest(action=CurtainsAction.Value(action))
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = CurtainStub(channel)
            response = client.SetAction(request, wait_for_ready=True)
            self.callback(response)
