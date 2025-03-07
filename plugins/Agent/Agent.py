from core.plugin.plugin_base import Plugin
from core.debug.logger import logger
import numpy as np

class Agent(Plugin):
    def _define_inputs(self) -> None:
        # The agent requires RSI data as input, expecting a (100,) array of floats.
        self._required_inputs = {"rsi": ((100,), float)}

    def _define_outputs(self) -> None:
        # This agent does not provide any outputs.
        self._provided_outputs = {}

    def build(self) -> None:
        logger.info(f"{self.__class__.__name__} build complete.")

    def process(self) -> None:
        logger.info(f"{self.__class__.__name__} processing data.")
        try:
            # Read RSI data from the "rsi" input port.
            rsi_data = self._inputs["rsi"].read()
            # Convert input data to a NumPy array for processing.
            rsi = np.array(rsi_data)
            # Use the last RSI value as the decision trigger.
            last_rsi = rsi[-1]
            if last_rsi < 30:
                decision = "BUY"
            elif last_rsi > 70:
                decision = "SELL"
            else:
                decision = "HOLD"
            decision_message = f"RSI value: {last_rsi:.2f}. Decision: {decision}."
            logger.info(decision_message)
            print(decision_message)
        except Exception as e:
            logger.error(f"Error in Agent processing: {e}")
