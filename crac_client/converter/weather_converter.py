import logging
import base64
import plotly.graph_objects as go
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
        logger.debug("weather_converter")
        logger.debug(response)
        if g_ui:
            if len(response.charts) > 0:
                charts = build_dict_from_chart_list(response.charts)
                
                # Mappa tra URN dei grafici e chiavi dei widget GUI
                chart_mapping = {
                    "weather.chart.wind": "wind-speed",
                    "weather.chart.wind_gust": "wind-gust-speed",
                    "weather.chart.temperature": "temperature",
                    "weather.chart.humidity": "humidity",
                    "weather.chart.rain_rate": "rain-rate",
                    "weather.chart.barometer": "barometer"
                }

                for urn, gui_key in chart_mapping.items():
                    if urn in charts:
                        try:
                            image_data = base64.b64encode(self.gauge(charts[urn]))
                            g_ui.win[gui_key](source=image_data)
                        except Exception as e:
                            logger.error(f"Errore nella generazione della gauge per {urn}: {e}")
                    else:
                        logger.warning(f"Grafico {urn} mancante nella risposta (probabilmente N/A)")
                        # Opzionale: pulire il widget o mettere un'immagine di placeholder "N/A"
                
                # Gestione speciale per il trend del barometro (testo invece di gauge)
                if "weather.chart.barometer_trend" in charts:
                    barometer_trend = charts["weather.chart.barometer_trend"]
                    g_ui.win["barometer-trend"](self.check_barometer_trend(barometer_trend))
                    g_ui.win["barometer-trend-forecast"](self.check_barometer_trend_forecast(barometer_trend))
                
                g_ui.win["weather-updated-at"](response.updated_at)
                g_ui.win["weather-interval"](response.interval)

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
            
            # Aggiornamento colori righe
            keys_to_color = ['wind-speed', 'wind-gust-speed', 'temperature', 'humidity', 'rain-rate', 'barometer']
            for k in keys_to_color:
                try:
                    g_ui.win[k].ParentRowFrame.config(background=background_color)
                except Exception:
                    pass

            try:
                g_ui.win["weather_block"].Widget.config(background=background_color)
                g_ui.win["weather_block"].Widget.config(highlightbackground=alert_background_color)
                g_ui.win["weather_block"].Widget.config(highlightcolor=alert_text_color)
            except Exception:
                pass

    def gauge(self, chart: Chart):
        fig = go.Figure(
            go.Indicator(
                domain={'x': [0, 1], 'y': [0, 1]},
                value=chart.value,
                mode="gauge+number+delta",
                title={'text': f"{chart.title} {chart.unit_of_measurement}", 'font': {'size': 65}},
                gauge={
                    'axis': {'range': [chart.min, chart.max]},
                    'bar': {'color': "darkslategray"},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "darkgray",
                    'steps': [self.build_range(threshold) for threshold in chart.thresholds],
                    'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 1, 'value': chart.value}
                }
            ),
            layout={"paper_bgcolor": 'lightslategrey', "font": {
                          'color': "white", 'family': "Helvetica", 'size': 35}}
        )

        return fig.to_image(format="png", scale=0.20)

    def build_range(self, threshold: Threshold):
        return {
            "range": [threshold.lower_bound, threshold.upper_bound],
            "color": self.get_color_by_type(threshold.threshold_type)
        }

    def get_color_by_type(self, type: ThresholdType):
        if (type == ThresholdType.THRESHOLD_TYPE_NORMAL):
            return "white"
        if (type == ThresholdType.THRESHOLD_TYPE_WARNING):
            return "orange"
        if (type == ThresholdType.THRESHOLD_TYPE_DANGER):
            return "red"
        return "white"
    
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
