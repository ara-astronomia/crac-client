import logging
from turtle import width
from crac_client.converter.converter import Converter
from crac_client.gui import Gui
from crac_protobuf.chart_pb2 import (
    Chart,
    WeatherResponse,
    Threshold,
)
import plotly.graph_objects as go
import base64


logger = logging.getLogger(__name__)


class WeatherConverter(Converter):
    def convert(self, response: WeatherResponse, g_ui: Gui):
        logger.debug("weathter_converter")
        logger.debug(response)
        if g_ui:
            wind_speed_image = base64.b64encode(self.gauge(response.wind_speed))
            wind_gust_speed_image = base64.b64encode(self.gauge(response.wind_gust_speed))
            temperature_image = base64.b64encode(self.gauge(response.temperature))
            humidity_image = base64.b64encode(self.gauge(response.humidity))
            rain_rate_image = base64.b64encode(self.gauge(response.rain_rate))
            barometer_image = base64.b64encode(self.gauge(response.barometer))
            g_ui.win["wind-speed"](source=wind_speed_image)
            g_ui.win["wind-gust-speed"](source=wind_gust_speed_image)
            g_ui.win["temperature"](source=temperature_image)
            g_ui.win["humidity"](source=humidity_image)
            g_ui.win["rain-rate"](source=rain_rate_image)
            g_ui.win["barometer"](source=barometer_image)
            g_ui.win["weather-updated-at"](response.updated_at)


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
                    'axis': {'range': [chart.thresholds[0].lower_bound, chart.thresholds[0].upper_bound]},
                    'bar': {'color': "darkslategray"},
                    'bgcolor': "white",
                    'borderwidth': 4,
                    'bordercolor': "darkgray",
                    'steps': [
                        {'range': [chart.thresholds[0].lower_bound,
                                   chart.thresholds[0].warning], 'color': "white"},
                        {'range': [chart.thresholds[0].warning,
                                   chart.thresholds[0].error], 'color': "orange"},
                        {'range': [
                            chart.thresholds[0].error, chart.thresholds[0].upper_bound], 'color': "red"},
                    ],
                    'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 1, 'value': chart.value}
                }
            )
        )

        fig.update_layout(paper_bgcolor='lightslategrey', font={
                          'color': "white", 'family': "Arial", 'size': 40})
        return fig.to_image(format="png", scale=0.25)
