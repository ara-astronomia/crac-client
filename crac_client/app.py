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

async def main_loop():
    g_ui = gui.Gui()
    roof_retriever = RoofRetriever(RoofConverter(g_ui))
    button_retriever = ButtonRetriever(ButtonConverter(g_ui))
    telescope_retriever = TelescopeRetriever(TelescopeConverter(g_ui))
    curtains_retriever = CurtainsRetriever(CurtainsConverter(g_ui))
    weather_retriever = WeatherRetriever(WeatherConverter(g_ui))
    background_tasks = set()

    while True:
        timeout = config.Config.getInt("sleep", "automazione")
        v, _ = g_ui.win.Read(timeout=timeout) # type: ignore
        logger.debug(f"Premuto pulsante: {v}")
        loop = asyncio.get_event_loop()
        match v:
            case v if v in [None, GuiKey.EXIT, GuiKey.SHUTDOWN]:
                g_ui = None
                await telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.TELESCOPE_DISCONNECT), autolight=False)
                break
            case ButtonKey.KEY_ROOF:
                task = loop.create_task(roof_retriever.setAction(action=g_ui.win[v].metadata)) 
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
            case v if v in ButtonRetriever.key_to_button_type_conversion.keys():
                task = loop.create_task(button_retriever.setAction(action=g_ui.win[v].metadata, key=v, g_ui=g_ui))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
            case v if v in TelescopeRetriever.key_to_telescope_action_conversion:
                task = loop.create_task(telescope_retriever.setAction(action=g_ui.win[v].metadata, autolight=g_ui.is_autolight()))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
            case v if v in CurtainsRetriever.key_to_curtains_action_conversion:
                task = loop.create_task(curtains_retriever.setAction(action=g_ui.win[v].metadata))
                background_tasks.add(task)
                task.add_done_callback(background_tasks.discard)
            case _:
                await asyncio.gather(
                    roof_retriever.setAction(action=RoofAction.Name(RoofAction.CHECK_ROOF)),
                    telescope_retriever.setAction(action=TelescopeAction.Name(TelescopeAction.CHECK_TELESCOPE), autolight=g_ui.is_autolight()),
                    curtains_retriever.setAction(action=CurtainsAction.Name(CurtainsAction.CHECK_CURTAIN)),
                    button_retriever.getStatus(),
                    weather_retriever.getStatus(g_ui.win["weather-updated-at"].get(), g_ui.win["weather-interval"].get())
                )
        
                
asyncio.run(main_loop())