
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.loc import _name
from crac_protobuf.button_pb2 import (
    ButtonAction,
    ButtonsResponse,
    ButtonResponse,
)


class ButtonConverter(Converter):
    def convert(self, response: ButtonResponse, g_ui: Gui):
    
        if g_ui is None:
            return

        if isinstance(response, (ButtonResponse)):
            self.button_convert(response, g_ui)
        elif isinstance(response, (ButtonsResponse)):
            self.buttons_convert(response, g_ui)
        
    def button_convert(self, response: ButtonResponse, g_ui: Gui):
        g_ui.win[response.button_gui.key](
            _name(response.button_gui.label), 
            disabled=response.button_gui.is_disabled,
            button_color=(
                response.button_gui.button_color.text_color, 
                response.button_gui.button_color.background_color
            )
        )
        g_ui.win[response.button_gui.key].metadata = ButtonAction.Name(response.button_gui.metadata)

    def buttons_convert(self, response: ButtonsResponse, g_ui: Gui):
        for button in response.buttons:
            self.convert(button, g_ui)
