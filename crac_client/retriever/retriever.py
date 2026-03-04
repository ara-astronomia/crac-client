from abc import ABC
import logging
from crac_client.converter.converter import Converter
from crac_client.jobs import JOBS


logger = logging.getLogger(__name__)


class Retriever(ABC):
    def __init__(self, converter: Converter, channel=None) -> None:
        self.converter = converter
        self.channel = channel

    def callback(self, call_future) -> None:
        logger.debug(f"DEBUG: Callback triggered for {self.__class__.__name__}")
        try:
            response = call_future.result()
            logger.info(f"SUCCESS: Received response for {self.__class__.__name__}")
            logger.debug(f"response to be converted is {response}")
        except BaseException as err:
            logger.error(f"FAILURE: The retrieval of the response for {self.__class__.__name__} threw an error {err=}, {type(err)=}")
            raise err
        else:
            JOBS.put({"convert": self.converter.convert, "response": response})
