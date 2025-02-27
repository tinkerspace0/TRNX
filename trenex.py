
import numpy as np

from core.namespace import RootNamespace
from core.shared_memory import SharedMemoryManager


if __name__=="__main__":
    trenex = RootNamespace()
    shmm = SharedMemoryManager()

    Exchange = trenex.create_namespace("Exchange")
    DataProcessor = trenex.create_namespace("DataProcessor")

    raw = Exchange.create_namespace("Raw")
    data = np.random.rand(100, 6)  # Shape (100,5)
    raw.set_item("ohlcv", shmm.create_block("ohlcv", data))
    
    print(shmm.ohlcv)
    shmm.close_all()

