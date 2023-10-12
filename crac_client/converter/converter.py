from abc import ABC, abstractmethod
from typing import Any

from crac_client.gui import Gui


class Converter(ABC):

    def __init__(self, g_ui: Gui) -> None:
        self.g_ui = g_ui

    @abstractmethod
    def convert(self, response: Any):
        raise NotImplementedError()

