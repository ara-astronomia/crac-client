import logging
import logging.config
from multiprocessing import Process, Queue

from crac_client.streaming import start_server, stop_server


logging.config.fileConfig('logging.conf')


from crac_client import config, gui
from crac_client.converter.button_converter import ButtonConverter
from crac_client.converter.camera_converter import CameraConverter
from crac_client.converter.curtains_converter import CurtainsConverter
from crac_client.converter.roof_converter import RoofConverter
from crac_client.converter.telescope_converter import TelescopeConverter
from crac_client.gui_constants import GuiKey
from crac_client.retriever.button_retriever import ButtonRetriever
from crac_client.retriever.camera_retriever import CameraRetriever
from crac_client.retriever.curtains_retriever import CurtainsRetriever
from crac_client.retriever.roof_retriever import RoofRetriever
from crac_client.retriever.telescope_retriever import TelescopeRetriever
from crac_protobuf.button_pb2 import ButtonKey
from crac_protobuf.camera_pb2 import CameraAction
from crac_protobuf.curtains_pb2 import CurtainsAction
from crac_protobuf.roof_pb2 import RoofAction
from crac_protobuf.telescope_pb2 import TelescopeAction


def deque(queue: Queue):
    while not queue.empty():
        try:
            logger.info("jobs is present")
            job = queue.get(False)
            job['convert'](job['response'], g_ui)
        except:
            logger.error("Error in retreiving job", exc_info=1)
            break
    else:
        logger.info("jobs is empty")

if __name__ ==  '__main__':
    queue = Queue()
    logger = logging.getLogger('crac_client.app')
    g_ui = gui.Gui()
    camera_retriever = CameraRetriever(CameraConverter(), queue)
    roof_retriever = RoofRetriever(RoofConverter(), queue)
    button_retriever = ButtonRetriever(ButtonConverter(), queue)
    telescope_retriever = TelescopeRetriever(TelescopeConverter(), queue)
    curtains_retriever = CurtainsRetriever(CurtainsConverter(), queue)
    camera1_process = Process(target=camera_retriever.setAction, args=(CameraAction.Name(CameraAction.CAMERA_CONNECT), "camera1"))
    camera1_process.start()
    camera2_process = Process(target=camera_retriever.setAction, args=(CameraAction.Name(CameraAction.CAMERA_CONNECT), "camera2"))
    camera2_process.start()
    camera1_process.join()
    camera2_process.join()
    video_process = Process(target=camera_retriever.listCameras)
    video_process.start()
    video_process.join()

    deque(queue)
    start_server()

    while True:
        timeout = config.Config.getInt("sleep", "automazione")
        v, _ = g_ui.win.Read(timeout=timeout)
        logger.debug(f"Premuto pulsante: {v}")
        match v:
            case v if v in [None, GuiKey.EXIT, GuiKey.SHUTDOWN]:
                g_ui = None
                Process(target=telescope_retriever.setAction, args=(TelescopeAction.Name(TelescopeAction.TELESCOPE_DISCONNECT), False,)).start()
                Process(target=camera_retriever.setAction, args=(CameraAction.Name(CameraAction.CAMERA_DISCONNECT), "camera1")).start()
                Process(target=camera_retriever.setAction, args=(CameraAction.Name(CameraAction.CAMERA_DISCONNECT), "camera2")).start()
                deque(queue)
                stop_server()
                break
            case ButtonKey.KEY_ROOF:
                Process(target=roof_retriever.setAction, args=(g_ui.win[v].metadata,)).start()
            case v if v in ButtonRetriever.key_to_button_type_conversion.keys():
                Process(target=button_retriever.setAction, args=(g_ui.win[v].metadata, v)).start()
            case v if v in TelescopeRetriever.key_to_telescope_action_conversion:
                Process(target=telescope_retriever.setAction, args=(g_ui.win[v].metadata, g_ui.is_autolight())).start()
            case v if v in CurtainsRetriever.key_to_curtains_action_conversion:
                Process(target=curtains_retriever.setAction, args=(g_ui.win[v].metadata,)).start()
            case ButtonKey.KEY_CAMERA1_DISPLAY:
                connection_button = g_ui.win[v]
                Process(target=camera_retriever.setAction, args=(connection_button.metadata, "camera1")).start()
            case ButtonKey.KEY_CAMERA2_DISPLAY:
                connection_button = g_ui.win[v]
                Process(target=camera_retriever.setAction, args=(connection_button.metadata, "camera2")).start()
            case _:
                Process(target=roof_retriever.setAction, args=(RoofAction.Name(RoofAction.CHECK_ROOF),)).start()
                Process(target=telescope_retriever.setAction, args=(TelescopeAction.Name(TelescopeAction.CHECK_TELESCOPE), g_ui.is_autolight())).start()
                Process(target=curtains_retriever.setAction, args=(CurtainsAction.Name(CurtainsAction.CHECK_CURTAIN),)).start()
                Process(target=camera_retriever.setAction, args=(CameraAction.Name(CameraAction.CAMERA_CHECK), "camera1")).start()
                Process(target=camera_retriever.setAction, args=(CameraAction.Name(CameraAction.CAMERA_CHECK), "camera2")).start()
                Process(target=button_retriever.getStatus).start()

        deque(queue)
