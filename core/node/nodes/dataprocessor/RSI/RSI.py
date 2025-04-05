
from core.node.node_param import Param

from core.node import Node


class RSI(Node):
    def __init__(self, name = None):
        super().__init__(name)

        self._static_params.limit = 50
        self._static_params.limit.set_allowed_range((10, 100))

        self._dynamic_params.period = Param("period", type(14), default_value=14, allowed_range=(10, 50), 
                                               description="Preiod at which RSI is to be calculated")

        self.update_io()

    def update_io(self):
        l = self._static_params.limit.value
        self._io_in.create_io("ohlcv", type(1.1), shape=(6, l))

        p = self._dynamic_params.period.value
        self._io_out.create_io("rsi", dtype=type(1.1), shape=(1,l-p-1))

    def process(self):
        pass