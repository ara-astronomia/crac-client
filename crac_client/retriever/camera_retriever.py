import logging
from crac_client.config import Config
from crac_client.gui import Gui
from crac_client.jobs import JOBS
from crac_client.retriever.retriever import Retriever
from crac_protobuf.camera_pb2 import (
    CameraAction,
    CameraRequest,
    CameraResponse,
    CamerasResponse,
)
from crac_protobuf.camera_pb2_grpc import (
    CameraStub,
)
import grpc


logger = logging.getLogger(__name__)


class CameraRetriever(Retriever):
    def __init__(self, converter) -> None:
        super().__init__(converter)
        self.channel = grpc.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = CameraStub(self.channel)

    def video(self, name: str) -> CameraResponse:
        return self.client.Video(CameraRequest(name=name), wait_for_ready=True)

    def setAction(self, action: str, g_ui: Gui, name: str) -> CameraResponse:
        camera_action = CameraAction.Value(action)
        if camera_action in (CameraAction.CAMERA_HIDE, CameraAction.CAMERA_SHOW) and g_ui:
            g_ui.set_autodisplay(False)
        if g_ui:
            autodisplay = g_ui.is_autodisplay()
        else:
            autodisplay = False
        request = CameraRequest(action=camera_action, name=name, autodisplay=autodisplay)
        response = self.client.SetAction(request, wait_for_ready=True)
        self.converter.convert(response, g_ui)

    def listCameras(self):
        call_future = self.client.ListCameras.future(CameraRequest())
        call_future.add_done_callback(self.callback_cameras_name)
    
    def callback_cameras_name(self, call_future) -> None:
        try:
            response = call_future.result()
            logger.info(f"response to be converted is {response}")
        except BaseException as err:
            logger.error(f"the retrieval of the response threw an error {err=}, {type(err)=}")
            raise err
        else:
            JOBS.append({"convert": self.converter.set_initial_cameras_status, "response": response})
            JOBS.append({"convert": self.converter.set_initial_retriever, "response": self})