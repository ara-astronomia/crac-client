import logging
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.gui_constants import GuiLabel
from crac_client.loc import _name
from crac_protobuf.curtains_pb2 import (
    CurtainStatus,
    CurtainOrientation,
    CurtainsResponse,
    CurtainsAction,
)


logger = logging.getLogger(__name__)


class CurtainsConverter(Converter):
    def convert(self, response: CurtainsResponse):

        if self.g_ui is None:
            return

        curtains_disabled = 0
        east_steps = 0
        west_steps = 0
        for curtain in response.curtains:
            orientation = CurtainOrientation.Name(curtain.orientation).lower()
            if curtain.orientation is CurtainOrientation.CURTAIN_EAST:
                east_steps = curtain.steps
            else:
                west_steps = curtain.steps

            if curtain.status in [CurtainStatus.CURTAIN_ERROR, CurtainStatus.CURTAIN_DANGER]:
                self.g_ui.status_alert(GuiLabel.ALERT_CHECK_CURTAINS_SWITCH.value)
                # self.g_ui.update_disable_button_close_roof()
                logger.debug("disabled close roof button")
            elif curtain.status is CurtainStatus.CURTAIN_DISABLED:
                self.g_ui.status_alert(GuiLabel.NO_ALERT.value)
                curtains_disabled += 1
            else:
                self.g_ui.status_alert(GuiLabel.NO_ALERT.value)
                # self.g_ui.update_disable_button_close_roof()
                logger.debug("disabled close roof button")

            self.g_ui.update_status_curtain(orientation, GuiLabel[CurtainStatus.Name(curtain.status)].value)

        for button_gui in response.buttons_gui:
            self.g_ui.win[button_gui.key](
                _name(button_gui.label),
                disabled=button_gui.is_disabled,
                button_color=(
                    button_gui.button_color.text_color, 
                    button_gui.button_color.background_color
                )
            )
            self.g_ui.win[button_gui.key].metadata = CurtainsAction.Name(button_gui.metadata)

        logger.debug(f"East steps: {east_steps}")
        logger.debug(f"West steps: {west_steps}")

        if self.g_ui.is_curtains_position_changed(east_steps, west_steps):
            alpha_e, alpha_w = self.g_ui.convert_steps_to_angular_values(east_steps, west_steps)
            self.g_ui.update_curtains_text(alpha_e, alpha_w)
            self.g_ui.update_curtains_graphic(alpha_e, alpha_w)
