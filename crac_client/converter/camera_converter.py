import logging
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.loc import _name
from crac_client.streaming import set_camera_status, set_cameras
from crac_protobuf.camera_pb2 import (
    CameraAction,
    CameraResponse,
    CamerasResponse,
    CameraStatus,
)


logger = logging.getLogger(__name__)


class CameraConverter(Converter):
    
    def convert(self, response: CameraResponse, g_ui: Gui):
        if response.status is CameraStatus.CAMERA_DISCONNECTED:
            set_camera_status(response.name, 0)
        else:
            set_camera_status(response.name, 1)
        
        if g_ui is None:
            return
        
        for button_gui in response.buttons_gui:
            g_ui.win[button_gui.key](
                _name(button_gui.label),
                disabled=button_gui.is_disabled,
                button_color=(
                    button_gui.button_color.text_color, 
                    button_gui.button_color.background_color
                )
            )
            g_ui.win[button_gui.key].metadata = CameraAction.Name(button_gui.metadata)
    
    def set_initial_cameras_status(self, response: CamerasResponse, g_ui: Gui):
        g_ui.win["camera-combo"].Update(values=("-- Scegli la camera --", response.camera1, response.camera2), value="-- Scegli la camera --")
        logger.debug(f"Combo value is: {g_ui.win['camera-combo'].get()}")
        set_cameras(
            {
                response.camera1: {
                    "key": "camera1", "status": 0
                }, 
                response.camera2: {
                    "key": "camera2", "status": 0
                }
            }
        )
