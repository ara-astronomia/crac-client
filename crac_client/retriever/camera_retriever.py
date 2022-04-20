import logging
from crac_client.config import Config
from crac_client.gui import Gui
from crac_client.jobs import JOBS
from crac_client.retriever.retriever import Retriever
from crac_protobuf.camera_pb2 import (
    CameraAction,
    CameraRequest,
    CameraResponse,
    Move,
)
from crac_protobuf.camera_pb2_grpc import (
    CameraStub,
)
from crac_protobuf.button_pb2 import (
    ButtonKey,
)
import grpc


logger = logging.getLogger(__name__)


class CameraRetriever(Retriever):
    def __init__(self, converter) -> None:
        super().__init__(converter)
        self.channel = grpc.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = CameraStub(self.channel)
    
    key_to_camera_move_conversion = {
        ButtonKey.KEY_CAMERA_STOP_MOVE,
        ButtonKey.KEY_CAMERA_MOVE_UP,
        ButtonKey.KEY_CAMERA_MOVE_TOP_RIGHT,
        ButtonKey.KEY_CAMERA_MOVE_RIGHT,
        ButtonKey.KEY_CAMERA_MOVE_BOTTOM_RIGHT,
        ButtonKey.KEY_CAMERA_MOVE_DOWN,
        ButtonKey.KEY_CAMERA_MOVE_BOTTOM_LEFT,
        ButtonKey.KEY_CAMERA_MOVE_LEFT,
        ButtonKey.KEY_CAMERA_MOVE_TOP_LEFT,
    }

    key_to_camera1_display_conversion = {
        ButtonKey.KEY_CAMERA1_CONNECTION,
        ButtonKey.KEY_CAMERA1_DISPLAY,
        ButtonKey.KEY_CAMERA1_IR_TOGGLE,
    }

    key_to_camera2_display_conversion = {
        ButtonKey.KEY_CAMERA2_CONNECTION,
        ButtonKey.KEY_CAMERA2_DISPLAY,
        ButtonKey.KEY_CAMERA2_IR_TOGGLE,
    }

    def video(self, name: str) -> CameraResponse:
        return self.client.Video(CameraRequest(name=name))

    def setAction(self, action: str, name: str, move: Move = None, g_ui: Gui = None) -> CameraResponse:
        camera_action = CameraAction.Value(action)
        if camera_action in (CameraAction.CAMERA_HIDE, CameraAction.CAMERA_SHOW) and g_ui:
            g_ui.set_autodisplay(False)
        if g_ui:
            autodisplay = g_ui.is_autodisplay()
        else:
            autodisplay = False
        request = CameraRequest(action=camera_action, name=name, move=move, autodisplay=autodisplay)
        call_future = self.client.SetAction.future(request, wait_for_ready=True)
        call_future.add_done_callback(self.callback)

    def listCameras(self):
        call_future = self.client.ListCameras.future(CameraRequest(), wait_for_ready=True)
        call_future.add_done_callback(self.callback_cameras_name)
    
    def callback_cameras_name(self, call_future) -> None:
        try:
            response = call_future.result()
            logger.info(f"response to be converted is {response}")
        except BaseException as err:
            logger.error(f"the retrieval of the response threw an error {err=}, {type(err)=}")
            raise err
        else:
            JOBS.put({"convert": self.converter.set_initial_cameras_status, "response": response})
            JOBS.put({"convert": self.converter.set_initial_retriever, "response": self})
