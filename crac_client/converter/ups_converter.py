import logging
from crac_client.converter import build_dict_from_chart_list
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_protobuf.chart_pb2 import (
    Chart,
    ChartStatus,
)
from crac_protobuf.ups_pb2 import (
    UpsResponse,
)
import PySimpleGUI as sg


logger = logging.getLogger(__name__)


class UpsConverter(Converter):
    def convert(self, response: UpsResponse, g_ui: Gui):
        logger.debug("weathter_converter")
        logger.debug(response)
        if g_ui and len(response.charts) > 0:
            charts = build_dict_from_chart_list(response.charts)
            self.update_progress_bar(g_ui.win, '_OUT-BATT-ROOM_', '_PERCENT-BATT-ROOM_', charts["ups.apc-3000.chart.battery"])
            self.update_progress_bar(g_ui.win, '_OUT-BATT-CUPOLA_', '_PERCENT-BATT-CUPOLA_', charts["ups.tecnoware-1000.chart.battery"])
            self.update_progress_bar(g_ui.win, '_OUT-VOLT-ROOM_', '_VOLT-ROOM_' , charts["ups.apc-3000.chart.voltage"])
            self.update_progress_bar(g_ui.win, '_OUT-VOLT-CUPOLA_', '_VOLT-CUPOLA_', charts["ups.tecnoware-1000.chart.voltage"])
                
    #change the update values ​​to those sent by crack-server
    def update_progress_bar(self, win, key1: str, key2: str, chart: Chart) -> None:
        background_color = sg.theme_background_color()
        if chart.status is ChartStatus.CHART_STATUS_NORMAL:
            text_color = "green"
        elif chart.status is ChartStatus.CHART_STATUS_WARNING:
            text_color = "gold"
        else:
            text_color = "red"
        win[key1](f"{round(chart.value, 2)} {chart.unit_of_measurement}", text_color=text_color, background_color=background_color)
        win[key2](chart.value-chart.min, bar_color=(text_color, background_color), max=chart.max-chart.min)
