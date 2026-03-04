import logging
import logging.config
import subprocess
logging.config.fileConfig('logging.conf')
from crac_client import config, gui
from crac_client.converter.button_converter import ButtonConverter
from crac_client.converter.curtains_converter import CurtainsConverter
from crac_client.converter.roof_converter import RoofConverter
from crac_client.converter.telescope_converter import TelescopeConverter
from crac_client.converter.ups_converter import UpsConverter
from crac_client.converter.weather_converter import WeatherConverter
from crac_client.gui_constants import GuiKey
from crac_client.jobs import JOBS
from crac_client.retriever.button_retriever import ButtonRetriever
from crac_client.retriever.curtains_retriever import CurtainsRetriever
from crac_client.retriever.roof_retriever import RoofRetriever
from crac_client.retriever.telescope_retriever import TelescopeRetriever
from crac_client.retriever.ups_retriever import UpsRetriever
from crac_client.retriever.weather_retriever import WeatherRetriever
from crac_protobuf.button_pb2 import ButtonKey
from crac_protobuf.curtains_pb2 import CurtainsAction
from crac_protobuf.roof_pb2 import RoofAction
from crac_protobuf.telescope_pb2 import TelescopeAction
from queue import Empty
from sys import platform
from time import sleep, time
from typing import Union


logger = logging.getLogger(__name__)


def blocking_deque():
    try:
        job = JOBS.get(block=True, timeout=10)
    except Empty as e:
        logger.error("The queue is empty", exc_info=1)
    else:
        job['convert'](job['response'], g_ui)
    deque()


def deque():
    if JOBS.qsize() > 0:
        logger.debug(f"Processamento di {JOBS.qsize()} lavori in coda...")
        while JOBS.qsize() > 0:
            try:
                job = JOBS.get()
                logger.debug(f"Esecuzione converter per {job['response'].__class__.__name__}")
                job['convert'](job['response'], g_ui)
            except Empty as e:
                logger.error("The queue is empty", exc_info=1)
        
        # Forza il refresh della finestra Tkinter
        if g_ui and g_ui.win:
            g_ui.win.refresh()

import grpc

g_ui = gui.Gui()
channel = grpc.insecure_channel(f'{config.Config.getValue("ip", "server")}:{config.Config.getValue("port", "server")}')
roof_retriever = RoofRetriever(RoofConverter(), channel=channel)
button_retriever = ButtonRetriever(ButtonConverter(), channel=channel)
telescope_retriever = TelescopeRetriever(TelescopeConverter(), channel=channel)
curtains_retriever = CurtainsRetriever(CurtainsConverter(), channel=channel)
ups_retriever = UpsRetriever(UpsConverter(), channel=channel)
weather_retriever = WeatherRetriever(WeatherConverter(), channel=channel)
weather_retriever.getStatus(g_ui.win["weather-updated-at"].get(), g_ui.win["weather-interval"].get())
# blocking_deque()  <-- Rimosso per evitare il freeze di 10s all'avvio

last_auto_polling = 0

while True:
    timeout = config.Config.getInt("sleep", "automazione")
    v, _ = g_ui.win.Read(timeout=timeout) # type: ignore
    
    now = time()
    
    match v:
        case v if v in [None, GuiKey.EXIT, GuiKey.SHUTDOWN]:
            g_ui = None
            telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.TELESCOPE_DISCONNECT), autolight=False)
            break
        case ButtonKey.KEY_ROOF:
            roof_retriever.setAction(action=g_ui.win[v].metadata)
        case v if v in ButtonRetriever.key_to_button_type_conversion.keys():
            button_retriever.setAction(action=g_ui.win[v].metadata, key=v, g_ui=g_ui)
        case v if v in TelescopeRetriever.key_to_telescope_action_conversion:
            telescope_retriever.setAction(action=g_ui.win[v].metadata, autolight=g_ui.is_autolight())
        case v if v in CurtainsRetriever.key_to_curtains_action_conversion:
            curtains_retriever.setAction(action=g_ui.win[v].metadata)
        case _:
            # Esegui il polling automatico solo ogni 5 secondi, non ad ogni iterazione del loop
            if now - last_auto_polling > 5:
                logger.debug("Esecuzione polling automatico (5s)")
                weather_retriever.getStatus(g_ui.win["weather-updated-at"].get(), g_ui.win["weather-interval"].get())
                ups_retriever.getStatus("", "")
                roof_retriever.setAction(action=RoofAction.Name(RoofAction.CHECK_ROOF))
                telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.CHECK_TELESCOPE), autolight=g_ui.is_autolight())
                curtains_retriever.setAction(action=CurtainsAction.Name(CurtainsAction.CHECK_CURTAIN))
                button_retriever.getStatus()
                last_auto_polling = now
            
    deque()
