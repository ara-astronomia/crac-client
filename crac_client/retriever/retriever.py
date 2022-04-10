from abc import ABC
import logging
from crac_client.converter.converter import Converter
from crac_client.jobs import JOBS


logger = logging.getLogger(__name__)


class Retriever(ABC):
    def __init__(self, converter: Converter) -> None:
        self.converter = converter

    def callback(self, call_future) -> None:
        try:
            response = call_future.result()
            logger.info(f"response to be converted is {response}")
        except BaseException as err:
            logger.error(f"the retrieval of the response threw an error {err=}, {type(err)=}")
            raise err
        else:
            JOBS.put({"convert": self.converter.convert, "response": response})
