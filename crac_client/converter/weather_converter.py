import logging
import base64
import plotly.graph_objects as go
import PySimpleGUI as sg
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
        logger.debug("weathter_converter")
        logger.debug(response)
        if g_ui:
            charts = self.build_dict_from_chart_list(response.charts)
            wind_speed_image = base64.b64encode(self.gauge(charts["weather.chart.wind"]))
            wind_gust_speed_image = base64.b64encode(self.gauge(charts["weather.chart.wind_gust"]))
            temperature_image = base64.b64encode(self.gauge(charts["weather.chart.temperature"]))
            humidity_image = base64.b64encode(self.gauge(charts["weather.chart.humidity"]))
            rain_rate_image = base64.b64encode(self.gauge(charts["weather.chart.rain_rate"]))
            barometer_image = base64.b64encode(self.gauge(charts["weather.chart.barometer"]))
            g_ui.win["wind-speed"](source=wind_speed_image)
            g_ui.win["wind-gust-speed"](source=wind_gust_speed_image)
            g_ui.win["temperature"](source=temperature_image)
            g_ui.win["humidity"](source=humidity_image)
            g_ui.win["rain-rate"](source=rain_rate_image)
            g_ui.win["barometer"](source=barometer_image)
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
            g_ui.win["weather_block"].Widget.config(background=background_color)
            g_ui.win["weather_block"].Widget.config(highlightbackground=alert_background_color)
            g_ui.win["weather_block"].Widget.config(highlightcolor=alert_text_color)

    def gauge(self, chart: Chart):
        fig = go.Figure(
            go.Indicator(
                domain={'x': [0, 1], 'y': [0, 1]},
                value=chart.value,
                mode="gauge+number+delta",
                title={'text': f"{chart.title} {chart.unit_of_measurement}", 'font': {'size': 65}},
                #delta={'reference': chart.thresholds[0].error, 'font': {
                #    'size': 60}, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
                gauge={
                    'axis': {'range': [chart.min, chart.max]},
                    'bar': {'color': "darkslategray"},
                    'bgcolor': "white",
                    'borderwidth': 1,
                    'bordercolor': "darkgray",
                    'steps': [self.build_range(threshold) for threshold in chart.thresholds],
                    'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 1, 'value': chart.value}
                }
            )
        )

        fig.update_layout(paper_bgcolor='lightslategrey', font={
                          'color': "white", 'family': "Arial", 'size': 35})
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

    def build_dict_from_chart_list(self, charts):
        return { chart.urn: chart for chart in charts }
