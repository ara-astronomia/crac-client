import logging

from numpy import size
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.jobs import ENABLED
from crac_client.loc import _name
from crac_client.retriever.retriever import Retriever
from crac_client.streaming import set_camera_status, set_cameras, set_retriever
from crac_protobuf.camera_pb2 import (
    CameraAction,
    CameraResponse,
    CamerasResponse,
    CameraStatus,
)


logger = logging.getLogger(__name__)


class CameraConverter(Converter):
    
    def convert(self, response: CameraResponse, g_ui: Gui):
        if ENABLED[response.name]:
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
        values = ["-- Scegli la camera --"]

        logger.debug(f"Camera list response is: {response}")

        if response.camera1.name:
            values.append(response.camera1.name)
            ENABLED["camera1"] = True
        if response.camera2.name:
            values.append(response.camera2.name)
            ENABLED["camera2"] = True
        
        if len(values) == 1:
            g_ui.win["camera-remote"](visible=False)
        else:
            g_ui.win["camera-combo"](values=("-- Scegli la camera --", response.camera1.name, response.camera2.name), value="-- Scegli la camera --")
            logger.debug(f"Combo value is: {g_ui.win['camera-combo'].get()}")
        
        logger.debug(f"Camera enabling value is: {ENABLED}")
        
        if not ENABLED["camera1"] or ENABLED["source1"]:
            g_ui.win["camera1"](visible=False)
        if not ENABLED["camera2"] or ENABLED["source1"]:
            g_ui.win["camera2"](visible=False)
    
        set_cameras(
            {
                response.camera1.name: {
                    "key": "camera1", "status": 0
                }, 
                response.camera2.name: {
                    "key": "camera2", "status": 0
                }
            }
        )
    
    def set_initial_retriever(self, retriever: Retriever, _: Gui):
        set_retriever(retriever=retriever)
