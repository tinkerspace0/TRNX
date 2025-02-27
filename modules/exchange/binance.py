import requests
import time
import hmac
import hashlib
from urllib.parse import urlencode
from modules.exchange.exchange_interface import ExchangeInterface
from core.utils.config_manager import ConfigManager
from core.debug.logger import logger
from core.debug.profiler import Profiler

class BinanceExchange(ExchangeInterface):
    """Handles communication with Binance API."""

    def __init__(self):
        self.config = ConfigManager.load_config("binance", module="exchange")
        self.api_key = self.config.get("api_key")
        self.secret_key = self.config.get("secret_key")
        self.base_url = self.config.get("base_url")
        self.endpoints = self.config.get("endpoints")

        if not self.api_key or not self.secret_key:
            raise ValueError("Missing Binance API credentials.")

    def _sign_request(self, params: dict) -> dict:
        """Signs the request using HMAC-SHA256 for authentication."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(self.secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        return params

    def _make_request(self, method: str, endpoint: str, params: dict = None, headers: dict = None):
        """Handles HTTP requests to Binance API."""
        url = f"{self.base_url}{endpoint}"
        headers = headers or {"X-MBX-APIKEY": self.api_key}
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            else:
                response = requests.post(url, json=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Binance API request failed: {e}")
            return None

    @Profiler.profile
    def fetch_ticker(self, symbol: str):
        """Fetch latest price for a trading pair."""
        endpoint = self.endpoints["ticker"]
        params = {"symbol": symbol.upper()}
        data = self._make_request("GET", endpoint, params)
        if data:
            logger.info(f"Fetched ticker for {symbol}: {data}")
            return {"symbol": symbol, "price": float(data["price"])}
        return None

    @Profiler.profile
    def fetch_ohlcv(self, symbol: str, timeframe: str, limit=100):
        """Fetch OHLCV (candlestick) data."""
        endpoint = self.endpoints["ohlcv"]
        params = {"symbol": symbol.upper(), "interval": timeframe, "limit": limit}
        data = self._make_request("GET", endpoint, params)
        if data:
            logger.info(f"Fetched {len(data)} OHLCV entries for {symbol} ({timeframe})")
            return [
                {
                    "timestamp": entry[0],
                    "open": float(entry[1]),
                    "high": float(entry[2]),
                    "low": float(entry[3]),
                    "close": float(entry[4]),
                    "volume": float(entry[5])
                }
                for entry in data
            ]
        return None

    @Profiler.profile
    def fetch_recent_trades(self, symbol: str, limit=20):
        """Fetch recent trades."""
        endpoint = self.endpoints["recent_trades"]
        params = {"symbol": symbol.upper(), "limit": limit}
        data = self._make_request("GET", endpoint, params)
        if data:
            logger.info(f"Fetched {len(data)} trades for {symbol}")
            return [
                {
                    "timestamp": trade["time"],
                    "price": float(trade["price"]),
                    "quantity": float(trade["qty"]),
                    "side": "buy" if trade["isBuyerMaker"] else "sell"
                }
                for trade in data
            ]
        return None

    @Profiler.profile
    def fetch_market_status(self):
        """Fetch Binance market status."""
        endpoint = self.endpoints["market_status"]
        data = self._make_request("GET", endpoint)
        if data:
            logger.info(f"Market status: {data}")
            return data
        return None

    @Profiler.profile
    def fetch_24h_volume(self, symbol: str):
        """Fetch 24-hour trading volume."""
        endpoint = self.endpoints["24h_volume"]
        params = {"symbol": symbol.upper()}
        data = self._make_request("GET", endpoint, params)
        if data:
            logger.info(f"24h volume for {symbol}: {data['volume']}")
            return {"symbol": symbol, "volume": float(data["volume"])}
        return None
