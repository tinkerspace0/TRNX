from core.plugin.plugin_base import Plugin
from core.debug.logger import logger

class Rsi(Plugin):
    def _define_inputs(self) -> None:
        # Define required input ports.
        self._required_inputs = {"ohlcv": ((100, 6), float)}

    def _define_outputs(self) -> None:
        # Define provided output ports.
        self._provided_outputs = {"rsi": ((100,), float)}


    def process(self) -> None:
        logger.info(f"{self.__class__.__name__} processing data.")
        print("Processing data")
