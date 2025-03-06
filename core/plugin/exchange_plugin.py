# core/plugin/exchange_plugin.py
from abc import abstractmethod
from typing import Dict, List
from core.plugin.plugin_base import Plugin
from core.debug.profiler import profile

class ExchangeInterface(Plugin):
    """
    Abstract interface for fetching essential market data from an exchange.
    """
    @profile
    @abstractmethod
    def fetch_ticker(self, symbol: str) -> Dict[str, float]:
        pass

    @profile
    @abstractmethod
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> List[List[float]]:
        pass

    @profile
    @abstractmethod
    def fetch_recent_trades(self, symbol: str, limit: int = 20) -> List[Dict[str, float]]:
        pass

    @profile
    @abstractmethod
    def fetch_order_book(self, symbol: str, depth: int = 10) -> Dict[str, List[List[float]]]:
        pass

    @profile
    @abstractmethod
    def fetch_market_status(self) -> Dict[str, str]:
        pass

    @profile
    @abstractmethod
    def fetch_24h_volume(self, symbol: str) -> Dict[str, float]:
        pass
