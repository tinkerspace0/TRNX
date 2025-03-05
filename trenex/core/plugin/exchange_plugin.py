from abc import ABC, abstractmethod
from typing import Dict, List

from core.debug.logger import logger
from core.debug.profiler import Profiler
from core.base.plugin_base import Plugin


class ExchangeInterface(Plugin):
    """
    Abstract interface for fetching essential market data from an exchange.
    """

    @Profiler.profile
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, float]:
        """
        Fetch the latest price for a given trading pair.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").

        Returns:
            Dict[str, float]: {"symbol": str, "price": float}
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[List[float]]:
        """
        Fetch historical OHLCV (candlestick) data.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").
            timeframe (str): The candlestick timeframe (e.g., "1m", "1h", "1d").
            limit (int, optional): Number of candles to retrieve. Default is 100.

        Returns:
            List[List[float]]: OHLCV data in the format:
            [
                [timestamp, open, high, low, close, volume],
                ...
            ]
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_recent_trades(self, symbol: str, limit: int = 20) -> List[Dict[str, float]]:
        """
        Fetch the most recent trades for a given trading pair.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").
            limit (int, optional): Number of recent trades to retrieve. Default is 20.

        Returns:
            List[Dict[str, float]]: Recent trades as:
            [
                {"timestamp": int, "price": float, "quantity": float, "side": "buy" or "sell"},
                ...
            ]
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_order_book(self, symbol: str, depth: int = 10) -> Dict[str, List[List[float]]]:
        """
        Fetch the current order book depth for a given trading pair.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").
            depth (int, optional): Number of levels to retrieve from the order book. Default is 10.

        Returns:
            Dict[str, List[List[float]]]: Order book structure:
            {
                "bids": [[price, quantity], ...],
                "asks": [[price, quantity], ...]
            }
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_market_status(self) -> Dict[str, str]:
        """
        Fetch the exchange market status (e.g., maintenance mode, operational status).

        Returns:
            Dict[str, str]: {"status": str, "message": str}
        """
        pass

    @Profiler.profile
    @abstractmethod
    def fetch_24h_volume(self, symbol: str) -> Dict[str, float]:
        """
        Fetch the 24-hour trading volume for a given asset.

        Args:
            symbol (str): The trading pair (e.g., "BTCUSDT").

        Returns:
            Dict[str, float]: {"symbol": str, "volume": float}
        """
        pass
