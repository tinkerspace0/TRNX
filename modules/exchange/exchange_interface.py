from abc import ABC, abstractmethod
from core.debug.logger import logger
from core.debug.profiler import Profiler

class ExchangeInterface(ABC):
    """Abstract interface for fetching essential market data from an exchange."""

    @Profiler.profile
    @abstractmethod
    def fetch_ticker(self, symbol: str):
        """
        Fetch the latest price for a given trading pair.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").

        Returns:
            dict: {"symbol": str, "price": float}
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100):
        """
        Fetch historical OHLCV (candlestick) data.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").
            timeframe (str): The candlestick timeframe (e.g., "1m", "1h", "1d").
            limit (int, optional): Number of candles to retrieve. Default is 100.

        Returns:
            list: List of OHLCV data as `[timestamp, open, high, low, close, volume]`.
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_recent_trades(self, symbol: str, limit: int = 20):
        """
        Fetch the most recent trades for a given trading pair.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").
            limit (int, optional): Number of recent trades to retrieve. Default is 20.

        Returns:
            list: List of recent trades as
            `[{"timestamp": int, "price": float, "quantity": float, "side": "buy" or "sell"}, ...]`
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_market_status(self):
        """
        Fetch the exchange market status (e.g., maintenance mode, operational status).

        Returns:
            dict: {"status": str, "message": str}
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_24h_volume(self, symbol: str):
        """
        Fetch the 24-hour trading volume for a given asset.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").

        Returns:
            dict: {"symbol": str, "volume": float}
        """
        pass
