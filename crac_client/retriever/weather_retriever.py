from datetime import datetime
import logging
from crac_client.config import Config
from crac_client.retriever.retriever import Retriever
from crac_protobuf.chart_pb2 import (
    WeatherRequest,
    WeatherResponse,
)
from crac_protobuf.chart_pb2_grpc import (
    WeatherStub,
)
import grpc


logger = logging.getLogger(__name__)


class WeatherRetriever(Retriever):
    def __init__(self, converter) -> None:
        super().__init__(converter)
        self.channel = grpc.aio.insecure_channel(f'{Config.getValue("ip", "server")}:{Config.getValue("port", "server")}')
        self.client = WeatherStub(self.channel)

    async def getStatus(self, latest_update: str, interval: str) -> WeatherResponse:
        logging.debug(f"latest update is {latest_update}")
        logging.debug(f"interval is {interval}")
        now = datetime.now()
        if (
            not interval or 
            not latest_update or 
            (now - datetime.fromtimestamp(int(latest_update))).seconds >= int(interval)
        ):
            response = await self.client.GetStatus(WeatherRequest(), wait_for_ready=True)
            self.converter.convert(response)
