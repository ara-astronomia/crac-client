import logging
import FreeSimpleGUI as sg
from crac_client.converter import build_dict_from_chart_list
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_protobuf.chart_pb2 import (
    Chart,
    WeatherResponse,
    Threshold,
    ThresholdType,
    WeatherStatus,
)


logger = logging.getLogger(__name__)


class WeatherConverter(Converter):
    def convert(self, response: WeatherResponse, g_ui: Gui):
        logger.debug("weather_converter (Text mode)")
        if not g_ui:
            return

        # Mappa tra URN dei grafici e chiavi dei widget GUI (sg.Text)
        chart_mapping = {
            "weather.chart.wind": "wind-speed",
            "weather.chart.wind_gust": "wind-gust-speed",
            "weather.chart.temperature": "temperature",
            "weather.chart.humidity": "humidity",
            "weather.chart.rain_rate": "rain-rate",
            "weather.chart.barometer": "barometer"
        }

        # Resettiamo a N/A prima di aggiornare con i nuovi dati
        for key in chart_mapping.values():
            g_ui.win[key].update("N/A")

        if len(response.charts) > 0:
            charts = build_dict_from_chart_list(response.charts)
            
            for urn, gui_key in chart_mapping.items():
                if urn in charts:
                    chart = charts[urn]
                    display_text = f"{chart.value} {chart.unit_of_measurement}"
                    g_ui.win[gui_key].update(display_text)
            
            # Gestione speciale per il trend del barometro
            if "weather.chart.barometer_trend" in charts:
                barometer_trend = charts["weather.chart.barometer_trend"]
                g_ui.win["barometer-trend"](self.check_barometer_trend(barometer_trend))
                g_ui.win["barometer-trend-forecast"](self.check_barometer_trend_forecast(barometer_trend))
            
            g_ui.win["weather-updated-at"](response.updated_at)
            g_ui.win["weather-interval"](response.interval)

        # Aggiornamento stato allerta
        alert = "CONDIZIONI METEO ADEGUATE"
        background_color = sg.theme_background_color()
        alert_background_color = "white"
        alert_text_color = "black"
        
        if response.status in (WeatherStatus.WEATHER_STATUS_WARNING, WeatherStatus.WEATHER_STATUS_UNSPECIFIED):
            if response.status == WeatherStatus.WEATHER_STATUS_UNSPECIFIED:
                alert = "CONDIZIONI METEO NON AGGIORNATE"
            else:
                alert = "CONDIZIONI DI OSSERVAZIONE AL LIMITE"
            background_color = "#ffa500"
            alert_background_color = background_color
            alert_text_color = "black"
        elif response.status == WeatherStatus.WEATHER_STATUS_DANGER:
            alert = "SISTEMA IN CHIUSURA PER METEO AVVERSA"
            background_color = "red"
            alert_background_color = background_color
            alert_text_color = "white"
        
        g_ui.win["alert_meteo"](alert, background_color=alert_background_color, text_color=alert_text_color)
        
        # Colorazione dello sfondo del blocco meteo per visibilità immediata
        try:
            g_ui.win["weather_block"].Widget.config(background=background_color)
        except Exception:
            pass

    def check_barometer_trend(self, barometer_trend: Chart):
        return f"{barometer_trend.value} {barometer_trend.unit_of_measurement}"

    def check_barometer_trend_forecast(self, barometer_trend: Chart):
        for threashold in barometer_trend.thresholds:
            if threashold.lower_bound <= barometer_trend.value <= threashold.upper_bound:
                if threashold.threshold_type == ThresholdType.THRESHOLD_TYPE_NORMAL:
                    return "Stabile per le prossime 12 ore"
                if threashold.threshold_type == ThresholdType.THRESHOLD_TYPE_WARNING:
                    return "In peggioramento entro le prossime 12 ore"
                if threashold.threshold_type == ThresholdType.THRESHOLD_TYPE_DANGER:
                    return "In peggioramento ora!"
        return "N/A"
