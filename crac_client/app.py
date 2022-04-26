import logging
import logging.config
logging.config.fileConfig('logging.conf')

import subprocess
from crac_client import config, gui
from crac_client.converter.button_converter import ButtonConverter
from crac_client.converter.camera_converter import CameraConverter
from crac_client.converter.curtains_converter import CurtainsConverter
from crac_client.converter.roof_converter import RoofConverter
from crac_client.converter.telescope_converter import TelescopeConverter
from crac_client.converter.weather_converter import WeatherConverter
from crac_client.gui_constants import GuiKey
from crac_client.jobs import JOBS, ENABLED
from crac_client.retriever.button_retriever import ButtonRetriever
from crac_client.retriever.camera_retriever import CameraRetriever
from crac_client.retriever.curtains_retriever import CurtainsRetriever
from crac_client.retriever.roof_retriever import RoofRetriever
from crac_client.retriever.telescope_retriever import TelescopeRetriever
from crac_client.retriever.weather_retriever import WeatherRetriever
from crac_client.streaming import start_server, stop_server
from crac_protobuf.button_pb2 import ButtonKey
from crac_protobuf.camera_pb2 import CameraAction
from crac_protobuf.curtains_pb2 import CurtainsAction
from crac_protobuf.roof_pb2 import RoofAction
from crac_protobuf.telescope_pb2 import TelescopeAction
from queue import Empty
from sys import platform
from time import sleep


def blocking_deque():
    try:
        job = JOBS.get(block=True, timeout=10)
    except Empty as e:
        logger.error("The queue is empty", exc_info=1)
    else:
        job['convert'](job['response'], g_ui)
    deque()


def deque():
    while JOBS.qsize() > 0:
        logger.debug(f"there are {JOBS.qsize()} jobs")
        try:
            job = JOBS.get()
        except Empty as e:
            logger.error("The queue is empt", exc_info=1)
        else:
            job['convert'](job['response'], g_ui)

def open_vlc(source: str):
    if platform == "linux" or platform == "linux2":
        return subprocess.Popen(["vlc", source])
    elif platform == "darwin":
        return subprocess.Popen(["open", "-na", "VLC", source])
    elif platform == "win32":
        return subprocess.Popen(["C:/Program Files/VideoLAN/VLC/vlc.exe", source])

def close_vlc(p: subprocess.Popen):
    if platform == "linux" or platform == "linux2":
        p.terminate()
    elif platform == "darwin":
        subprocess.Popen("osascript -e 'quit app \"VLC\"'", shell=True)
    elif platform == "win32":
        p.terminate()

def __backend_streaming(enabled: list, source1: str, source2: str) -> bool:
    (enabled['camera1'] or enabled['camera2']) and (not source1 or not source2)


logger = logging.getLogger('crac_client.app')
g_ui = gui.Gui()
roof_retriever = RoofRetriever(RoofConverter())
button_retriever = ButtonRetriever(ButtonConverter())
telescope_retriever = TelescopeRetriever(TelescopeConverter())
curtains_retriever = CurtainsRetriever(CurtainsConverter())
camera_retriever = CameraRetriever(CameraConverter())
weather_retriever = WeatherRetriever(WeatherConverter())
camera_retriever.listCameras()
blocking_deque()
logger.debug(f"ENABLED is {ENABLED}")
source1 = config.Config.getValue("source", "camera1")
source2 = config.Config.getValue("source", "camera2")
logger.debug(f"ENABLED is {ENABLED['camera1']} and source1 is {source1}")
logger.debug(f"ENABLED is {ENABLED['camera2']} and source2 is {source2}")
if source1:
    stream1 = open_vlc(source1)
if source2:
    stream2 = open_vlc(source2)
camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_IR_DISABLE), name="camera1", g_ui=g_ui)
camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_CONNECT), name="camera1", g_ui=g_ui) 
camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_IR_DISABLE), name="camera2", g_ui=g_ui)
camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_CONNECT), name="camera2", g_ui=g_ui)
blocking_deque()

if __backend_streaming(ENABLED, source1, source2):
    start_server()

while True:
    timeout = config.Config.getInt("sleep", "automazione")
    v, _ = g_ui.win.Read(timeout=timeout)
    logger.debug(f"Premuto pulsante: {v}")
    match v:
        case v if v in [None, GuiKey.EXIT, GuiKey.SHUTDOWN]:
            g_ui = None
            telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.TELESCOPE_DISCONNECT), autolight=False)
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_DISCONNECT), name="camera1", g_ui=g_ui)
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_IR_AUTO), name="camera1", g_ui=g_ui)
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_DISCONNECT), name="camera2", g_ui=g_ui)
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_IR_AUTO), name="camera2", g_ui=g_ui)
            blocking_deque()
            if __backend_streaming(ENABLED, source1, source2):
                stop_server()
            if source1:
                sleep(1)
                close_vlc(stream1)
            if source2:
                sleep(1)
                close_vlc(stream2)
            break
        case ButtonKey.KEY_ROOF:
            roof_retriever.setAction(action=g_ui.win[v].metadata)
        case v if v in ButtonRetriever.key_to_button_type_conversion.keys():
            button_retriever.setAction(action=g_ui.win[v].metadata, key=v, g_ui=g_ui)
        case v if v in TelescopeRetriever.key_to_telescope_action_conversion:
            telescope_retriever.setAction(action=g_ui.win[v].metadata, autolight=g_ui.is_autolight())
        case v if v in CurtainsRetriever.key_to_curtains_action_conversion:
            curtains_retriever.setAction(action=g_ui.win[v].metadata)
        case ButtonKey.KEY_CAMERA1_DISPLAY:
            connection_button = g_ui.win[v]
            camera_retriever.setAction(action=connection_button.metadata, name="camera1", g_ui=g_ui)
        case ButtonKey.KEY_CAMERA2_DISPLAY:
            connection_button = g_ui.win[v]
            camera_retriever.setAction(action=connection_button.metadata, name="camera2", g_ui=g_ui)
        case v if v in CameraRetriever.key_to_camera_move_conversion:
            move_button = g_ui.win[v]
            camera_name = g_ui.win.find_element('camera-combo').Get()
            logger.debug(f"Camera name is: {camera_name}")
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_MOVE), name=camera_name, move=move_button.metadata, g_ui=g_ui)
        case ButtonKey.KEY_CAMERA1_IR_TOGGLE:
            camera_retriever.setAction(action=g_ui.win[v].metadata, name="camera1", g_ui=g_ui)
        case ButtonKey.KEY_CAMERA2_IR_TOGGLE:
            camera_retriever.setAction(action=g_ui.win[v].metadata, name="camera2", g_ui=g_ui)
        case _:
            roof_retriever.setAction(action=RoofAction.Name(RoofAction.CHECK_ROOF))
            telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.CHECK_TELESCOPE), autolight=g_ui.is_autolight())
            curtains_retriever.setAction(action=CurtainsAction.Name(CurtainsAction.CHECK_CURTAIN))
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_CHECK), name="camera1", g_ui=g_ui)
            camera_retriever.setAction(action=CameraAction.Name(CameraAction.CAMERA_CHECK), name="camera2", g_ui=g_ui)
            button_retriever.getStatus()
            weather_retriever.getStatus(g_ui.win["weather-updated-at"].get())
            
    deque()
