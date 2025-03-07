from core.plugin import ExchangeInterface
from core.debug.logger import logger

class Binance(ExchangeInterface):
    def _define_inputs(self) -> None:
        # Define required input ports (if any).
        self._required_inputs = {}

    def _define_outputs(self) -> None:
        # Define provided output ports.
        self._provided_outputs = {
            "ticker": ((2,), float),
            "ohlcv": ((100, 6), float),
            }

    def fetch_ticker(self, symbol: str) -> None:
        logger.info(f"Fetching ticker for {symbol}")
        print("Fetching ticker for {symbol}")
        # Write ticker data to shared memory, e.g.:
        # self._outputs['ticker'].write(data)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> None:
        logger.info(f"Fetching OHLCV for {symbol}")
        print("Fetching OHLCV for {symbol}")
        # Write OHLCV data to shared memory

    def fetch_recent_trades(self, symbol: str, limit: int = 20) -> None:
        logger.info(f"Fetching recent trades for {symbol}")
        # Write recent trades data to shared memory

    def fetch_order_book(self, symbol: str, depth: int = 10) -> None:
        logger.info(f"Fetching order book for {symbol}")
        # Write order book data to shared memory

    def fetch_market_status(self) -> None:
        logger.info("Fetching market status")
        # Write market status to shared memory

    def fetch_24h_volume(self, symbol: str) -> None:
        logger.info(f"Fetching 24h volume for {symbol}")
        # Write 24h volume data to shared memory

    def process(self) -> None:
        print("Processing data")
        self.fetch_ticker("BTCUSDT")
        self.fetch_ohlcv("BTCUSDT", "1m")