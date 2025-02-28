import requests
import time
import hmac
import hashlib
import numpy as np
from urllib.parse import urlencode
from modules.exchange.exchange_interface import ExchangeInterface
from core.utils.config_manager import ConfigManager
from core.debug.logger import logger
from core.debug.profiler import Profiler
from core.shared_memory import SharedMemoryManager
from core.namespace import RootNamespace

class BinanceExchange(ExchangeInterface):
    """Handles communication with Binance API and stores market data in shared memory."""

    def __init__(self):
        self.config = ConfigManager.load_config("binance", module="exchange")
        self.api_key = self.config.get("api_key")
        self.secret_key = self.config.get("secret_key")
        self.base_url = self.config.get("base_url")
        self.endpoints = self.config.get("endpoints")

        # Create universal Exchange namespace
        self.namespace = RootNamespace().Exchange.Binance
        self.shared_memory = SharedMemoryManager()

        # Create shared memory blocks for each type of data
        self._initialize_memory_blocks()

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials.")

    def _initialize_memory_blocks(self):
        """Initialize shared memory blocks for Binance market data."""
        if "Ticker" not in self.namespace:
            self.namespace.Ticker = self.shared_memory.create_block("Binance_Ticker", np.zeros((10, 2)))  # [Symbol, Price]
        if "OHLCV" not in self.namespace:
            self.namespace.OHLCV = self.shared_memory.create_block("Binance_OHLCV", np.zeros((100, 6)))  # [Time, Open, High, Low, Close, Volume]
        if "RecentTrades" not in self.namespace:
            self.namespace.RecentTrades = self.shared_memory.create_block("Binance_Trades", np.zeros((50, 4)))  # [Time, Price, Quantity, Side]
        if "Volume" not in self.namespace:
            self.namespace.Volume = self.shared_memory.create_block("Binance_Volume", np.zeros((10, 2)))  # [Symbol, Volume]
        if "MarketStatus" not in self.namespace:
            self.namespace.MarketStatus = self.shared_memory.create_block("Binance_MarketStatus", np.zeros((1, 2)))  # [Status, Message]

    def _make_request(self, method: str, endpoint: str, params: dict = None):
        """Handles HTTP requests to Binance API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}

        try:
            response = requests.get(url, params=params, headers=headers) if method == "GET" else requests.post(url, json=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance API request failed: {e}")
            return None

    @Profiler.profile
    def fetch_ticker(self, symbol: str):
        """Fetch latest price and update shared memory block."""
        endpoint = self.endpoints["ticker"]
        params = {"symbol": symbol.upper()}
        data = self._make_request("GET", endpoint, params)

        if data:
            ticker_data = np.array([[symbol, float(data["price"])]])
            self.shared_memory.write("Binance_Ticker", ticker_data)
            logger.info(f"Updated shared memory: Exchange.Binance.Ticker ({symbol})")
            return ticker_data
        return None

    @Profiler.profile
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit=100):
        """Fetch OHLCV data and update shared memory block."""
        endpoint = self.endpoints["ohlcv"]
        params = {"symbol": symbol.upper(), "interval": timeframe, "limit": limit}
        data = self._make_request("GET", endpoint, params)

        if data:
            ohlcv_data = np.array([
                [entry[0], float(entry[1]), float(entry[2]), float(entry[3]), float(entry[4]), float(entry[5])]
                for entry in data
            ])
            self.shared_memory.write("Binance_OHLCV", ohlcv_data)
            logger.info(f"Updated shared memory: Exchange.Binance.OHLCV ({symbol})")
            return ohlcv_data
        return None

    @Profiler.profile
    def fetch_recent_trades(self, symbol: str, limit=20):
        """Fetch recent trades and update shared memory block."""
        endpoint = self.endpoints["recent_trades"]
        params = {"symbol": symbol.upper(), "limit": limit}
        data = self._make_request("GET", endpoint, params)

        if data:
            trades_data = np.array([
                [trade["time"], float(trade["price"]), float(trade["qty"]), 1 if trade["isBuyerMaker"] else 0]
                for trade in data
            ])
            self.shared_memory.write("Binance_Trades", trades_data)
            logger.info(f"Updated shared memory: Exchange.Binance.RecentTrades ({symbol})")
            return trades_data
        return None

    @Profiler.profile
    def fetch_market_status(self):
        """Fetch Binance market status and update shared memory block."""
        endpoint = self.endpoints["market_status"]
        data = self._make_request("GET", endpoint)

        if data:
            market_status_data = np.array([[data["status"], data["message"]]])
            self.shared_memory.write("Binance_MarketStatus", market_status_data)
            logger.info("Updated shared memory: Exchange.Binance.MarketStatus")
            return data
        return None

    @Profiler.profile
    def fetch_24h_volume(self, symbol: str):
        """Fetch 24-hour trading volume and update shared memory block."""
        endpoint = self.endpoints["24h_volume"]
        params = {"symbol": symbol.upper()}
        data = self._make_request("GET", endpoint, params)

        if data:
            volume_data = np.array([[symbol, float(data["volume"])]])
            self.shared_memory.write("Binance_Volume", volume_data)
            logger.info(f"Updated shared memory: Exchange.Binance.Volume ({symbol})")
            return volume_data
        return None
