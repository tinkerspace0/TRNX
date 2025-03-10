import numpy as np

from core.plugin.types.data_plugins import DataPlugin
from core.debug.logger import logger

class Rsi(DataPlugin):
    def _define_inputs(self) -> None:
        logger.info('Executing _define_inputs in Rsi')
        # Expecting OHLCV data: shape (100, 6), where column 4 is the close price.
        self._required_inputs = {"ohlcv": ((100, 6), float)}

    def _define_outputs(self) -> None:
        logger.info('Executing _define_outputs in Rsi')
        # The output "rsi" is a 1D array with 100 float values.
        self._provided_outputs = {"rsi": ((100,), float)}

    def compute(self, prices: np.ndarray, period: int = 14) -> np.ndarray:
        """
        Compute the Relative Strength Index (RSI) for an array of prices.
        prices: 1D numpy array of close prices.
        period: Number of periods for RSI calculation.
        Returns a 1D numpy array of RSI values, with the first `period` values set to 0.
        """
        prices = prices.astype(float)
        delta = np.diff(prices)
        rsi = np.zeros_like(prices)
        if len(prices) < period + 1:
            return rsi  # Not enough data
        # Calculate gains and losses
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        # Initial average gain and loss
        avg_gain = np.mean(gain[:period])
        avg_loss = np.mean(loss[:period])
        # Calculate RSI for the period-th element
        if avg_loss == 0:
            rsi[period] = 100
        else:
            rs = avg_gain / avg_loss
            rsi[period] = 100 - (100 / (1 + rs))
        # Use smoothing formula for subsequent elements
        for i in range(period + 1, len(prices)):
            avg_gain = (avg_gain * (period - 1) + gain[i - 1]) / period
            avg_loss = (avg_loss * (period - 1) + loss[i - 1]) / period
            if avg_loss == 0:
                rsi[i] = 100
            else:
                rs = avg_gain / avg_loss
                rsi[i] = 100 - (100 / (1 + rs))
        # Set the first 'period' values to 0 (undefined RSI)
        rsi[:period] = 0
        return rsi
    
    def process(self) -> None:
        logger.info('Executing process in Rsi')
        logger.info(f"{self.__class__.__name__} processing data.")
        try:
            # Read OHLCV data from the input port "ohlcv"
            # Expecting a NumPy array of shape (100, 6)
            ohlcv = self._inputs["ohlcv"].read()
            if ohlcv is None or ohlcv.shape[0] < 1:
                logger.error("No OHLCV data available.")
                return
            # Extract close prices (assuming column index 4 is 'close')
            closes = ohlcv[:, 4]
            # Compute RSI with a period of 14
            rsi_values = self.compute(closes, period=14)
            # Write RSI values to the output port "rsi"
            # Convert to list if necessary, depending on your shared memory port API
            self._write_output("rsi", rsi_values.tolist())
            logger.info(f"RSI computed and written: {rsi_values}")
        except Exception as e:
            logger.error(f"Error processing RSI: {e}")

