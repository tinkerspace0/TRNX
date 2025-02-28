import requests
import numpy as np
from modules.exchange.exchange_interface import ExchangeInterface
from core.utils.config_manager import ConfigManager
from core.debug.logger import logger
from core.debug.profiler import Profiler
from core.shared_memory import SharedMemoryPort
from core.namespace import RootNamespace

class BinanceExchange(ExchangeInterface):
    """Handles communication with Binance API and stores market data in shared memory."""

    def __init__(self):
        self.config = ConfigManager.load_config("binance", module="exchange")
        self.api_key = self.config.get("api_key")
        self.secret_key = self.config.get("secret_key")
        self.base_url = self.config.get("base_url")
        self.endpoints = self.config.get("endpoints")

        # Use a generic exchange namespace
        self.namespace = RootNamespace().Exchange.Current

        # Create shared memory blocks for each type of data
        self._initialize_memory_ports()

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials.")

    def _initialize_memory_ports(self):
        """Initialize shared memory ports for exchange market data."""
        if "Ticker" not in self.namespace:
            self.namespace.Ticker = SharedMemoryPort("Exchange_Ticker", (1, 2))  # [Symbol, Price]
        if "OHLCV" not in self.namespace:
            self.namespace.OHLCV = SharedMemoryPort("Exchange_OHLCV", (100, 6))  # [Time, Open, High, Low, Close, Volume]
        if "RecentTrades" not in self.namespace:
            self.namespace.RecentTrades = SharedMemoryPort("Exchange_Trades", (50, 4))  # [Time, Price, Quantity, Side]
        if "Volume" not in self.namespace:
            self.namespace.Volume = SharedMemoryPort("Exchange_Volume", (1, 2))  # [Symbol, Volume]
        if "MarketStatus" not in self.namespace:
            self.namespace.MarketStatus = SharedMemoryPort("Exchange_MarketStatus", (1, 2))  # [Status, Message]

    def _make_request(self, method: str, endpoint: str, params: dict = None):
        """Handles HTTP requests to Binance API."""
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key}

        try:
            response = requests.get(url, params=params, headers=headers) if method == "GET" else requests.post(url, json=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Exchange API request failed: {e}")
            return None

    @Profiler.profile
    def fetch_ticker(self, symbol: str):
        """Fetch latest price and update shared memory port."""
        endpoint = self.endpoints["ticker"]
        params = {"symbol": symbol.upper()}
        data = self._make_request("GET", endpoint, params)

        if data:
            ticker_data = np.array([[symbol, float(data["price"])]])
            self.namespace.Ticker.write(ticker_data)
            logger.info(f"Updated shared memory: Exchange.Current.Ticker ({symbol})")
            return ticker_data
        return None

    @Profiler.profile
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit=100):
        """Fetch OHLCV data and update shared memory port."""
        endpoint = self.endpoints["ohlcv"]
        params = {"symbol": symbol.upper(), "interval": timeframe, "limit": limit}
        data = self._make_request("GET", endpoint, params)

        if data:
            ohlcv_data = np.array([
                [entry[0], float(entry[1]), float(entry[2]), float(entry[3]), float(entry[4]), float(entry[5])]
                for entry in data
            ])
            self.namespace.OHLCV.write(ohlcv_data)
            logger.info(f"Updated shared memory: Exchange.Current.OHLCV ({symbol})")
            return ohlcv_data
        return None

    @Profiler.profile
    def fetch_recent_trades(self, symbol: str, limit=20):
        """Fetch recent trades and update shared memory port."""
        endpoint = self.endpoints["recent_trades"]
        params = {"symbol": symbol.upper(), "limit": limit}
        data = self._make_request("GET", endpoint, params)

        if data:
            trades_data = np.array([
                [trade["time"], float(trade["price"]), float(trade["qty"]), 1 if trade["isBuyerMaker"] else 0]
                for trade in data
            ])
            self.namespace.RecentTrades.write(trades_data)
            logger.info(f"Updated shared memory: Exchange.Current.RecentTrades ({symbol})")
            return trades_data
        return None

    @Profiler.profile
    def fetch_order_book(self, symbol: str, depth: int = 10):
        """Fetch order book and update shared memory port."""
        endpoint = self.endpoints["order_book"]
        params = {"symbol": symbol.upper(), "limit": depth}
        data = self._make_request("GET", endpoint, params)

        if data:
            bids = np.array([[float(bid[0]), float(bid[1])] for bid in data["bids"][:depth]])
            asks = np.array([[float(ask[0]), float(ask[1])] for ask in data["asks"][:depth]])
            order_book_data = np.vstack((bids, asks))  # Stack bids & asks
            self.namespace.OrderBook = SharedMemoryPort("Exchange_OrderBook", order_book_data.shape)
            self.namespace.OrderBook.write(order_book_data)

            logger.info(f"Updated shared memory: Exchange.Current.OrderBook ({symbol})")
            return order_book_data
        return None

    @Profiler.profile
    def fetch_market_status(self):
        """Fetch exchange market status and update shared memory port."""
        endpoint = self.endpoints["market_status"]
        data = self._make_request("GET", endpoint)

        if data:
            market_status_data = np.array([[data["status"], data["message"]]])
            self.namespace.MarketStatus.write(market_status_data)
            logger.info("Updated shared memory: Exchange.Current.MarketStatus")
            return data
        return None

    @Profiler.profile
    def fetch_24h_volume(self, symbol: str):
        """Fetch 24-hour trading volume and update shared memory port."""
        endpoint = self.endpoints["24h_volume"]
        params = {"symbol": symbol.upper()}
        data = self._make_request("GET", endpoint, params)

        if data:
            volume_data = np.array([[symbol, float(data["volume"])]])
            self.namespace.Volume.write(volume_data)
            logger.info(f"Updated shared memory: Exchange.Current.Volume ({symbol})")
            return volume_data
        return None
