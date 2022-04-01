from abc import ABC
from multiprocessing import Queue
import logging
from crac_client.converter.converter import Converter
from crac_client.jobs import JOBS, MJOBS


logger = logging.getLogger(__name__)


class Retriever(ABC):
    def __init__(self, converter: Converter, queue: Queue) -> None:
        self.converter = converter
        self._queue = queue

    def callback(self, response) -> None:
        self._queue.put({"convert": self.converter.convert, "response": response})
