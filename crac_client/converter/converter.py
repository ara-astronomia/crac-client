from abc import ABC, abstractmethod
from typing import Any

from crac_client.gui import Gui


class Converter(ABC):

    @abstractmethod
    def convert(self, response: Any, g_ui: Gui):
        raise NotImplementedError()

