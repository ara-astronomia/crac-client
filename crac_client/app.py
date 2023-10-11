import logging
import logging.config
logging.config.fileConfig('logging.conf')
import asyncio

from crac_client import config, gui
from crac_client.converter.button_converter import ButtonConverter
from crac_client.converter.curtains_converter import CurtainsConverter
from crac_client.converter.roof_converter import RoofConverter
from crac_client.converter.telescope_converter import TelescopeConverter
from crac_client.converter.weather_converter import WeatherConverter
from crac_client.gui_constants import GuiKey
from crac_client.jobs import JOBS
from crac_client.retriever.button_retriever import ButtonRetriever
from crac_client.retriever.curtains_retriever import CurtainsRetriever
from crac_client.retriever.roof_retriever import RoofRetriever
from crac_client.retriever.telescope_retriever import TelescopeRetriever
from crac_client.retriever.weather_retriever import WeatherRetriever
from crac_protobuf.button_pb2 import ButtonKey
from crac_protobuf.curtains_pb2 import CurtainsAction
from crac_protobuf.roof_pb2 import RoofAction
from crac_protobuf.telescope_pb2 import TelescopeAction
from queue import Empty


logger = logging.getLogger(__name__)


async def deque(g_ui: gui.Gui):
        while JOBS.qsize() > 0:
            logger.debug(f"there are {JOBS.qsize()} jobs")
            try:
                job = JOBS.get()
            except Empty as e:
                logger.error("The queue is empty", exc_info=1)
            else:
                job['convert'](job['response'], g_ui)

async def main_loop():

    g_ui = gui.Gui()
    roof_retriever = RoofRetriever(RoofConverter())
    button_retriever = ButtonRetriever(ButtonConverter())
    telescope_retriever = TelescopeRetriever(TelescopeConverter())
    curtains_retriever = CurtainsRetriever(CurtainsConverter())
    weather_retriever = WeatherRetriever(WeatherConverter())

    while True:
        timeout = config.Config.getInt("sleep", "automazione")
        v, _ = g_ui.win.Read(timeout=timeout) # type: ignore
        logger.debug(f"Premuto pulsante: {v}")
        match v:
            case v if v in [None, GuiKey.EXIT, GuiKey.SHUTDOWN]:
                g_ui = None
                await telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.TELESCOPE_DISCONNECT), autolight=False)
                break
            case ButtonKey.KEY_ROOF:
                await roof_retriever.setAction(action=g_ui.win[v].metadata)
            case v if v in ButtonRetriever.key_to_button_type_conversion.keys():
                await button_retriever.setAction(action=g_ui.win[v].metadata, key=v, g_ui=g_ui)
            case v if v in TelescopeRetriever.key_to_telescope_action_conversion:
                await telescope_retriever.setAction(action=g_ui.win[v].metadata, autolight=g_ui.is_autolight())
            case v if v in CurtainsRetriever.key_to_curtains_action_conversion:
                await curtains_retriever.setAction(action=g_ui.win[v].metadata)
            case _:
                await asyncio.gather(
                    roof_retriever.setAction(action=RoofAction.Name(RoofAction.CHECK_ROOF)),
                    telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.CHECK_TELESCOPE), autolight=g_ui.is_autolight()),
                    curtains_retriever.setAction(action=CurtainsAction.Name(CurtainsAction.CHECK_CURTAIN)),
                    button_retriever.getStatus(),
                    weather_retriever.getStatus(g_ui.win["weather-updated-at"].get(), g_ui.win["weather-interval"].get())
                )
                
        await deque(g_ui)

asyncio.run(main_loop())