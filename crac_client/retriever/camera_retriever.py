import logging
from multiprocessing import Queue
from crac_client.config import Config
from crac_client.gui import Gui
from crac_client.retriever.retriever import Retriever
from crac_protobuf.camera_pb2 import (
    CameraAction,
    CameraRequest,
    CameraResponse,
)
from crac_protobuf.camera_pb2_grpc import (
    CameraStub,
)
import grpc


logger = logging.getLogger(__name__)


class CameraRetriever(Retriever):
    def __init__(self, converter, queue: Queue) -> None:
        super().__init__(converter, queue)

    def video(self, name: str) -> CameraResponse:
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = CameraStub(channel)
            return client.Video(CameraRequest(name=name))

    def setAction(self, action: str, name: str, g_ui: Gui = None) -> CameraResponse:
        camera_action = CameraAction.Value(action)
        # if camera_action in (CameraAction.CAMERA_HIDE, CameraAction.CAMERA_SHOW) and g_ui:
        #     g_ui.set_autodisplay(False)
        if g_ui:
            autodisplay = g_ui.is_autodisplay()
        else:
            autodisplay = False
        request = CameraRequest(action=camera_action, name=name, autodisplay=autodisplay)
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = CameraStub(channel)
            response = client.SetAction(request, wait_for_ready=True)
            self.callback(response)

    def listCameras(self):
        with grpc.insecure_channel(
            f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}',
            options=[
                ("grpc.max_send_message_length", -1),
                ("grpc.max_receive_message_length", -1),
                ("grpc.so_reuseport", 1),
                ("grpc.use_local_subchannel_pool", 1),
            ],
        ) as channel:
            client = CameraStub(channel)
            response = client.ListCameras(CameraRequest(), wait_for_ready=True)
            self.callback_cameras_name(response)
    
    def callback_cameras_name(self, response) -> None:
        self._queue.put({"convert": self.converter.set_initial_cameras_status, "response": response})
