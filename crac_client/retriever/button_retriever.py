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
    def __init__(self, converter: Converter) -> None:
        super().__init__(converter)
        self.channel = grpc.aio.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = ButtonStub(self.channel)

    key_to_button_type_conversion = {
        ButtonKey.KEY_TELE_SWITCH: ButtonType.TELE_SWITCH,
        ButtonKey.KEY_CCD_SWITCH: ButtonType.CCD_SWITCH,
        ButtonKey.KEY_FLAT_LIGHT: ButtonType.FLAT_LIGHT,
        ButtonKey.KEY_DOME_LIGHT: ButtonType.DOME_LIGHT,
    }

    async def setAction(self, action: str, key: ButtonKey, g_ui: Gui):
        if key is ButtonKey.KEY_DOME_LIGHT and g_ui:
            g_ui.set_autolight(False)
        request = ButtonRequest(action=ButtonAction.Value(action), type=ButtonRetriever.key_to_button_type_conversion[key])
        response = await self.client.SetAction(request, wait_for_ready=True)
        self.converter.convert(response)

    async def getStatus(self):
        response = await self.client.GetStatus(ButtonsRequest(), wait_for_ready=True)
        self.converter.convert(response)
