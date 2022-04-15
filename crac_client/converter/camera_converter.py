import logging
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_client.jobs import ENABLED
from crac_client.loc import _name
from crac_client.retriever.retriever import Retriever
from crac_client.streaming import set_camera_status, set_cameras, set_retriever
from crac_protobuf.button_pb2 import (
    ButtonKey,
)
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
    
        logger.debug(f"the response value for is visible is {response.buttons_gui}")
        if g_ui is None:
            return
        
        if (
            ButtonKey.KEY_CAMERA1_CONNECTION not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA1_DISPLAY not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA1_IR_TOGGLE not in ENABLED["camera1"]
        ):
            g_ui.win["camera1"](visible = False)
        else:
            g_ui.win["camera1"](visible = True)

        if (
            ButtonKey.KEY_CAMERA2_CONNECTION not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA2_DISPLAY not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA2_IR_TOGGLE not in ENABLED["camera2"]
        ):
            g_ui.win["camera2"](visible = False)
        else:
            g_ui.win["camera2"](visible = True)

        if (
            ButtonKey.KEY_CAMERA1_DISPLAY not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA2_DISPLAY not in ENABLED["camera2"]
        ):
            g_ui.win["cameras-autodisplay"](visible = False)
        else:
            g_ui.win["cameras-autodisplay"](visible = True)

        if (
            ButtonKey.KEY_CAMERA_STOP_MOVE not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_UP not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_TOP_RIGHT not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_RIGHT not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_RIGHT not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_DOWN not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_LEFT not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_LEFT not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_MOVE_TOP_LEFT not in ENABLED["camera1"] and
            ButtonKey.KEY_CAMERA_STOP_MOVE not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_UP not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_TOP_RIGHT not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_RIGHT not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_RIGHT not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_DOWN not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_LEFT not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_LEFT not in ENABLED["camera2"] and
            ButtonKey.KEY_CAMERA_MOVE_TOP_LEFT not in ENABLED["camera2"]
        ):
            g_ui.win["camera-remote"](visible = False)
        else:
            g_ui.win["camera-remote"](visible = True)

        for button_gui in response.buttons_gui:
            g_ui.win[button_gui.key](
                _name(button_gui.label),
                disabled=button_gui.is_disabled,
                visible=button_gui.is_visible,
                button_color=(
                    button_gui.button_color.text_color, 
                    button_gui.button_color.background_color
                )
            )
            g_ui.win[button_gui.key].metadata = CameraAction.Name(button_gui.metadata)
    
    def set_initial_cameras_status(self, response: CamerasResponse, g_ui: Gui):
        values = ["-- Scegli la camera --"]

        logger.debug(f"Camera1 list response is: {response.camera1.features}")
        logger.debug(f"Camera2 list response is: {response.camera2.features}")

        if response.camera1.name:
            values.append(response.camera1.name)
            ENABLED["camera1"] = response.camera1.features
        if response.camera2.name:
            values.append(response.camera2.name)
            ENABLED["camera2"] = response.camera2.features

        combo_names = ["-- Scegli la camera --"]

        if (
            ButtonKey.KEY_CAMERA_STOP_MOVE in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_UP in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_TOP_RIGHT in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_RIGHT in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_RIGHT in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_DOWN in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_LEFT in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_LEFT in ENABLED["camera1"] or
            ButtonKey.KEY_CAMERA_MOVE_TOP_LEFT in ENABLED["camera1"]
        ):
            combo_names.append(response.camera1.name)
        
        if (
            ButtonKey.KEY_CAMERA_STOP_MOVE in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_UP in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_TOP_RIGHT in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_RIGHT in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_RIGHT in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_DOWN in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_BOTTOM_LEFT in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_LEFT in ENABLED["camera2"] or
            ButtonKey.KEY_CAMERA_MOVE_TOP_LEFT in ENABLED["camera2"]
        ):
            combo_names.append(response.camera2.name)
        
        if len(values) == 1:
            g_ui.win["camera-remote"](visible=False)
        else:
            g_ui.win["camera-combo"](values=combo_names, value=combo_names[0])
            logger.debug(f"Combo value is: {g_ui.win['camera-combo'].get()}")
        logger.debug(f"Camera enabling value is: {ENABLED}")
    
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
