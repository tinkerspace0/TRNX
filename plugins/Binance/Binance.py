import requests

from core.plugin import ExchangeInterface
from core.debug.logger import logger

class Binance(ExchangeInterface):
    def _define_inputs(self) -> None:
        # Define required input ports (if any).
        self._required_inputs = {}

    def _define_outputs(self) -> None:
        # Define provided output ports with their shapes and data types.
        # "ticker": 1 float value (e.g., price)
        # "ohlcv": 100 rows x 6 columns (open_time, open, high, low, close, volume)
        # "recent_trades": 20 rows x 6 columns (trade_id, price, qty, quoteQty, time, isBuyerMaker)
        # "order_book": 20 rows x 4 columns (bid_price, bid_qty, ask_price, ask_qty)
        # "market_status": 1 float (1.0 = operational, 0.0 = non-operational)
        # "volume_24h": 1 float (24-hour trading volume)
        self._provided_outputs = {
            "ticker": ((1,), float),
            "ohlcv": ((100, 6), float),
            "recent_trades": ((20, 6), float),
            "order_book": ((20, 4), float),
            "market_status": ((1,), float),
            "volume_24h": ((1,), float)
        }

    def fetch_ticker(self, symbol: str) -> None:
        logger.info(f"Fetching ticker for {symbol}")
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/price",
                params={"symbol": symbol}
            )
            data = response.json()
            price = float(data.get("price", 0))
            ticker_data = [price]  # Expecting shape (1,)
            self._write_output("ticker", ticker_data)
            logger.info(f"Ticker data written: {ticker_data}")
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> None:
        logger.info(f"Fetching OHLCV for {symbol} with interval {timeframe}")
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/klines",
                params={"symbol": symbol, "interval": timeframe, "limit": limit}
            )
            data = response.json()  # Each kline is a list of values.
            ohlcv_data = []
            for kline in data:
                # Take the first 6 values: [open_time, open, high, low, close, volume]
                row = [float(x) for x in kline[:6]]
                ohlcv_data.append(row)
            # Pad with zeros if necessary to reach 'limit' rows.
            while len(ohlcv_data) < limit:
                ohlcv_data.append([0.0] * 6)
            self._write_output("ohlcv", ohlcv_data)
            logger.info("OHLCV data written.")
        except Exception as e:
            logger.error(f"Error fetching OHLCV: {e}")

    def fetch_recent_trades(self, symbol: str, limit: int = 20) -> None:
        logger.info(f"Fetching recent trades for {symbol}")
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/trades",
                params={"symbol": symbol, "limit": limit}
            )
            data = response.json()  # List of trade objects.
            trades_data = []
            for trade in data:
                # For each trade, extract: id, price, qty, quoteQty, time, isBuyerMaker (convert boolean to 1.0 or 0.0)
                trade_id = float(trade.get("id", 0))
                price = float(trade.get("price", 0))
                qty = float(trade.get("qty", 0))
                quoteQty = float(trade.get("quoteQty", 0))
                trade_time = float(trade.get("time", 0))
                isBuyerMaker = 1.0 if trade.get("isBuyerMaker", False) else 0.0
                trades_data.append([trade_id, price, qty, quoteQty, trade_time, isBuyerMaker])
            # Pad with zeros if fewer than 'limit' rows.
            while len(trades_data) < limit:
                trades_data.append([0.0] * 6)
            self._write_output("recent_trades", trades_data)
            logger.info("Recent trades data written.")
        except Exception as e:
            logger.error(f"Error fetching recent trades: {e}")

    def fetch_order_book(self, symbol: str, depth: int = 10) -> None:
        logger.info(f"Fetching order book for {symbol}")
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/depth",
                params={"symbol": symbol, "limit": depth}
            )
            data = response.json()  # Returns dict with "bids" and "asks"
            bids = data.get("bids", [])
            asks = data.get("asks", [])
            # Combine into one array: each row [bid_price, bid_qty, ask_price, ask_qty]
            order_book_data = []
            for i in range(depth):
                if i < len(bids):
                    bid_price = float(bids[i][0])
                    bid_qty = float(bids[i][1])
                else:
                    bid_price, bid_qty = 0.0, 0.0
                if i < len(asks):
                    ask_price = float(asks[i][0])
                    ask_qty = float(asks[i][1])
                else:
                    ask_price, ask_qty = 0.0, 0.0
                order_book_data.append([bid_price, bid_qty, ask_price, ask_qty])
            self._write_output("order_book", order_book_data)
            logger.info("Order book data written.")
        except Exception as e:
            logger.error(f"Error fetching order book: {e}")

    def fetch_market_status(self) -> None:
        logger.info("Fetching market status")
        try:
            # Binance does not have a dedicated market status endpoint.
            # We use exchangeInfo as a proxy. If successful, we assume the market is operational.
            response = requests.get("https://api.binance.com/api/v3/exchangeInfo")
            status = 1.0 if response.status_code == 200 else 0.0
            self._write_output("market_status", [status])
            logger.info("Market status data written.")
        except Exception as e:
            logger.error(f"Error fetching market status: {e}")

    def fetch_24h_volume(self, symbol: str) -> None:
        logger.info(f"Fetching 24h volume for {symbol}")
        try:
            response = requests.get(
                "https://api.binance.com/api/v3/ticker/24hr",
                params={"symbol": symbol}
            )
            data = response.json()
            volume = float(data.get("volume", 0))
            self._write_output("volume_24h", [volume])
            logger.info(f"24h volume data written: {volume}")
        except Exception as e:
            logger.error(f"Error fetching 24h volume: {e}")

    def process(self) -> None:
        logger.info("Processing data in Binance plugin")
        self.fetch_ticker("BTCUSDT")
        self.fetch_ohlcv("BTCUSDT", "1m")
        self.fetch_recent_trades("BTCUSDT", 20)
        self.fetch_order_book("BTCUSDT", 20)
        self.fetch_market_status()
        self.fetch_24h_volume("BTCUSDT")