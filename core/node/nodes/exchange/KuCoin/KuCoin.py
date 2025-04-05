

from core.node.node_param import Param
from core.node import Node


class KuCoin(Node):
    def __init__(self, name = None):
        super().__init__(name)

        self._static_params.limit = 100
        self._static_params.limit = 500
        self._static_params.limit.set_allowed_range((10, 1000))

        self._dynamic_params.timeframe = Param("timeframe", type("5m"), default_value="5m", allowed_values=["1m", "5m", "15m", "30m", "1h"], 
                                               description="Timeframe of the market data to be fetched from")

        self.update_io()

    def update_io(self):
        # l = self._static_params.limit.value
        # self._io_out.create_io("ohlcv", type(1.1), shape=(6, l))
        pass
    def process(self):
        pass