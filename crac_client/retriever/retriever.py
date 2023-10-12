from abc import ABC
import logging
from crac_client.converter.converter import Converter
from crac_client.jobs import JOBS


logger = logging.getLogger(__name__)


class Retriever(ABC):
    def __init__(self, converter: Converter) -> None:
        self.converter = converter
