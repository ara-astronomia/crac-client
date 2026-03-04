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
        if not g_ui or not g_ui.win:
            return

        # Mappa tra URN dei grafici e chiavi dei widget GUI (sg.Image)
        chart_mapping = {
            "weather.chart.wind": ("wind-speed", "Vento"),
            "weather.chart.wind_gust": ("wind-gust-speed", "Raffica"),
            "weather.chart.temperature": ("temperature", "Temp."),
            "weather.chart.humidity": ("humidity", "Umidità"),
            "weather.chart.rain_rate": ("rain-rate", "Pioggia"),
            "weather.chart.barometer": ("barometer", "Barom.")
        }

        charts = build_dict_from_chart_list(response.charts)
        
        for urn, (gui_key, title) in chart_mapping.items():
            try:
                if urn in charts:
                    chart = charts[urn]
                    image_bytes = self.gauge(chart)
                else:
                    image_bytes = self.na_gauge(title)
                
                image_base64_str = base64.b64encode(image_bytes).decode('utf-8')
                g_ui.win[gui_key].update(data=image_base64_str)
            except Exception as e:
                logger.error(f"Errore aggiornamento grafico {gui_key}: {e}")
        
        # Trend barometro (testo)
        if "weather.chart.barometer_trend" in charts:
            bt = charts["weather.chart.barometer_trend"]
            g_ui.win["barometer-trend"].update(self.check_barometer_trend(bt))
            g_ui.win["barometer-trend-forecast"].update(self.check_barometer_trend_forecast(bt))
        else:
            g_ui.win["barometer-trend"].update("N/A")
            g_ui.win["barometer-trend-forecast"].update("N/A")
        
        g_ui.win["weather-updated-at"].update(response.updated_at)
        g_ui.win["weather-interval"].update(response.interval)

        # Stato Allerta
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
        
        g_ui.win["alert_meteo"].update(alert, background_color=alert_background_color, text_color=alert_text_color)
        
        try:
            g_ui.win["weather_block"].Widget.config(background=background_color)
        except: pass

    def gauge(self, chart: Chart):
        fig = go.Figure(
            go.Indicator(
                domain={'x': [0, 1], 'y': [0, 0.85]},
                value=chart.value,
                mode="gauge+number",
                title={
                    'text': f"{chart.title}<br><span style='font-size:0.7em'>{chart.unit_of_measurement}</span>", 
                    'font': {'size': 18},
                    'align': 'center'
                },
                gauge={
                    'axis': {'range': [chart.min, chart.max], 'tickwidth': 1, 'tickcolor': "white"},
                    'bar': {'color': "darkslategray"}, # Ripristinato originale
                    'bgcolor': "white", # Ripristinato originale
                    'borderwidth': 1,
                    'bordercolor': "darkgray", # Ripristinato originale
                    'steps': [self.build_range(threshold) for threshold in chart.thresholds],
                    'threshold': {'line': {'color': "black", 'width': 3}, 'thickness': 0.75, 'value': chart.value} # Ripristinato originale
                }
            ),
            layout={
                "paper_bgcolor": '#000033', # Sfondo Blu Notte solo per l'immagine
                "font": {'color': "white", 'family': "Helvetica"},
                "width": 150, "height": 150, 
                "margin": {'t': 60, 'b': 5, 'l': 15, 'r': 15} 
            }
        )
        return fig.to_image(format="png", scale=1.0)

    def na_gauge(self, title: str):
        """ Genera un'immagine di segnaposto per i dati mancanti """
        fig = go.Figure(
            layout={
                "paper_bgcolor": '#000033', # Sfondo Blu Notte
                "width": 150, "height": 150,
                "annotations": [{
                    "text": f"{title}<br><br><span style='font-size:1.5em'>N/A</span>",
                    "showarrow": False,
                    "font": {"size": 18, "color": "white", "family": "Helvetica"}
                }],
                "margin": {'t': 10, 'b': 10, 'l': 10, 'r': 10}
            }
        )
        return fig.to_image(format="png", scale=1.0)

    def build_range(self, threshold: Threshold):
        return {
            "range": [threshold.lower_bound, threshold.upper_bound],
            "color": self.get_color_by_type(threshold.threshold_type)
        }

    def get_color_by_type(self, type: ThresholdType):
        # Ripristinati i colori originali delle soglie
        if (type == ThresholdType.THRESHOLD_TYPE_NORMAL): return "white"
        if (type == ThresholdType.THRESHOLD_TYPE_WARNING): return "orange"
        if (type == ThresholdType.THRESHOLD_TYPE_DANGER): return "red"
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
