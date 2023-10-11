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
    def __init__(self, converter: Converter) -> None:
        super().__init__(converter)
        self.channel = grpc.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = TelescopeStub(self.channel)

    key_to_telescope_action_conversion = (
        ButtonKey.KEY_SYNC,
        ButtonKey.KEY_PARK,
        ButtonKey.KEY_FLAT,
        ButtonKey.KEY_TELESCOPE_CONNECTION_TOGGLE,
    )

    async def setAction(self, action: str, autolight: bool):
        request = TelescopeRequest(action=TelescopeAction.Value(action), autolight=autolight)
        call_future = self.client.SetAction.future(request, wait_for_ready=True)
        call_future.add_done_callback(self.callback)
