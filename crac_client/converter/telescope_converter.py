import logging
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.gui_constants import GuiLabel
from crac_client.loc import _name
from crac_protobuf.telescope_pb2 import (
    TelescopeStatus,
    TelescopeSpeed,
    TelescopeResponse,
    TelescopeAction,
)


logger = logging.getLogger(__name__)


class TelescopeConverter(Converter):
    def convert(self, response: TelescopeResponse, g_ui: Gui):
        if g_ui is None:
            return
        if response.speed is TelescopeSpeed.SPEED_NOT_TRACKING:
            g_ui.update_status_tracking(GuiLabel.TELESCOPE_TRACKING_OFF.value, text_color="red", background_color="white")
            g_ui.update_status_slewing(GuiLabel.TELESCOPE_SLEWING_OFF.value, text_color="red", background_color="white")
        elif response.speed is TelescopeSpeed.SPEED_TRACKING:
            g_ui.update_status_tracking(GuiLabel.TELESCOPE_TRACKING_ON.value, text_color="#2c2825", background_color="green")
            g_ui.update_status_slewing(GuiLabel.TELESCOPE_SLEWING_OFF.value, text_color="red", background_color="white")
        elif response.speed is TelescopeSpeed.SPEED_CENTERING or response.speed is TelescopeSpeed.SPEED_ERROR:
            g_ui.update_status_tracking(GuiLabel.TELESCOPE_TRACKING_OFF.value, text_color="red", background_color="white")
            g_ui.update_status_slewing(GuiLabel.TELESCOPE_SLEWING_OFF.value, text_color="red", background_color="white")
        elif response.speed is TelescopeSpeed.SPEED_SLEWING:
            g_ui.update_status_tracking(GuiLabel.TELESCOPE_TRACKING_OFF.value, text_color="red", background_color="white")
            g_ui.update_status_slewing(GuiLabel.TELESCOPE_SLEWING_ON.value, text_color="#2c2825", background_color="green")

        if response.status is TelescopeStatus.PARKED:
            g_ui.update_status_tele(GuiLabel.TELESCOPE_PARKED.value, text_color="red", background_color="white")
        elif response.status is TelescopeStatus.FLATTER:
            g_ui.update_status_tele(GuiLabel.TELESCOPE_FLATTER.value, text_color="red", background_color="white")
        elif response.status is TelescopeStatus.SECURE:
            g_ui.update_status_tele(GuiLabel.TELESCOPE_SECURED.value, text_color="red", background_color="white")
        elif response.status is TelescopeStatus.DISCONNECTED:
            g_ui.update_status_tele(GuiLabel.TELESCOPE_DISCONNECTED.value, text_color="red", background_color="white")
        elif response.status is TelescopeStatus.LOST:
            g_ui.update_status_tele(GuiLabel.TELESCOPE_ANOMALY.value)
            g_ui.status_alert(GuiLabel.ALERT_TELESCOPE_LOST.value)
        elif response.status is TelescopeStatus.ERROR:
            g_ui.update_status_tele(GuiLabel.TELESCOPE_ERROR.value)
            g_ui.status_alert(GuiLabel.ALERT_TELESCOPE_ERROR.value)
        else:
            cardinal = vars(GuiLabel).get(f"TELESCOPE_{TelescopeStatus.Name(response.status)}").value
            g_ui.update_status_tele(cardinal, text_color="#2c2825", background_color="green")

        for button_gui in response.buttons_gui:
            g_ui.win[button_gui.key](
                _name(button_gui.label),
                disabled=button_gui.is_disabled,
                button_color=(
                    button_gui.button_color.text_color, 
                    button_gui.button_color.background_color
                )
            )
            g_ui.win[button_gui.key].metadata = TelescopeAction.Name(button_gui.metadata)

        logger.debug(f"Altaz coords: {response.aa_coords}")
        print(f"Airmass: {response.airmass}")
        logger.debug(f"Transit: {response.transit}")
        logger.debug(f"Time To Transit: {response.time_to_transit}")
        logger.debug(f"coords alt: {response.aa_coords.alt}")
        g_ui.update_tele_text({"alt": response.aa_coords.alt, "az": response.aa_coords.az})
        g_ui.update_airmass({"airmass": response.airmass})
