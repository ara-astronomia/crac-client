from multiprocessing import Queue
from crac_client.config import Config
from crac_client.converter.converter import Converter
from crac_client.retriever.retriever import Retriever
from crac_protobuf.button_pb2 import (
    ButtonKey,
)
from crac_protobuf.telescope_pb2 import (
    TelescopeAction,
    TelescopeRequest,
)
from crac_protobuf.telescope_pb2_grpc import TelescopeStub
import grpc


class TelescopeRetriever(Retriever):
    def __init__(self, converter: Converter, queue: Queue) -> None:
        super().__init__(converter, queue)


    key_to_telescope_action_conversion = [
        ButtonKey.KEY_SYNC,
        ButtonKey.KEY_PARK,
        ButtonKey.KEY_FLAT,
        ButtonKey.KEY_TELESCOPE_CONNECTION_TOGGLE,
    ]

    def setAction(self, action: str, autolight: bool):
        request = TelescopeRequest(action=TelescopeAction.Value(action), autolight=autolight)
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],    
        ) as channel:
            client = TelescopeStub(channel)
            response = client.SetAction(request, wait_for_ready=True)
            self.callback(response)
