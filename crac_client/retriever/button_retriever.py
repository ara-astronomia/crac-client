from multiprocessing import Queue
from crac_client.config import Config
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.retriever.retriever import Retriever
from crac_protobuf.button_pb2 import (
    ButtonAction,
    ButtonType,
    ButtonRequest,
    ButtonsRequest,
    ButtonKey,
)
from crac_protobuf.button_pb2_grpc import (
    ButtonStub,
)
import grpc


class ButtonRetriever(Retriever):
    def __init__(self, converter: Converter, queue: Queue) -> None:
        super().__init__(converter, queue)

    key_to_button_type_conversion = {
        ButtonKey.KEY_TELE_SWITCH: ButtonType.TELE_SWITCH,
        ButtonKey.KEY_CCD_SWITCH: ButtonType.CCD_SWITCH,
        ButtonKey.KEY_FLAT_LIGHT: ButtonType.FLAT_LIGHT,
        ButtonKey.KEY_DOME_LIGHT: ButtonType.DOME_LIGHT,
    }

    def setAction(self, action: str, key: ButtonKey, g_ui: Gui = None):
        # if key is ButtonKey.KEY_DOME_LIGHT and g_ui:
        #     g_ui.set_autolight(False)
        request = ButtonRequest(action=ButtonAction.Value(action), type=ButtonRetriever.key_to_button_type_conversion[key])
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = ButtonStub(channel)
            response = client.SetAction(request, wait_for_ready=True)
            self.callback(response)

    def getStatus(self):
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = ButtonStub(channel)
            response = client.GetStatus(ButtonsRequest(), wait_for_ready=True)
            self.callback(response)
