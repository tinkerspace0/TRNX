import numpy as np
from multiprocessing import shared_memory, Lock
from core.identity import IDGenerator
from core.debug.logger import logger
from core.debug.profiler import Profiler  
import threading
import atexit

class SharedMemoryManager:
    """
    Singleton manager for handling shared memory dynamically.
    - Allows direct attribute-style access (`manager.some_block = data`).
    - Blocks are referenced by **names**, but can also be retrieved via block IDs.
    - Thread-safe, prevents memory corruption.
    """

    _instance = None
    _lock = threading.Lock()  # Ensures thread safety

    def __new__(cls):
        """Ensure Singleton instance."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SharedMemoryManager, cls).__new__(cls)
                cls._instance._initialize()
                # Register cleanup when the program exits
                atexit.register(cls._instance.unlink_all)
                logger.info("SharedMemoryManager initialized.")
        return cls._instance

    @Profiler.profile  
    def _initialize(self):
        """Initialize internal storage for shared memory blocks."""
        self._blocks = {}  # Stores name -> (SharedMemory instance, shape, dtype, block_id)
        self._id_map = {}  # Stores block_id -> name
        self._locks = {}   # Stores name -> Lock
        logger.debug("SharedMemoryManager storage initialized.")

    @Profiler.profile  
    def create_block(self, name: str, data: np.ndarray) -> str:
        """
        Create a new shared memory block with a given name and return its block ID.
        """
        if name in self._blocks:
            logger.warning(f"Attempted to create block '{name}', but it already exists.")
            raise ValueError(f"Block '{name}' already exists.")

        block_id = IDGenerator.generate_id()
        shape, dtype = data.shape, data.dtype
        nbytes = np.prod(shape) * dtype.itemsize

        try:
            shm = shared_memory.SharedMemory(name=block_id, create=True, size=nbytes)
            array = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
            np.copyto(array, data)

            self._blocks[name] = (shm, shape, dtype, block_id)
            self._id_map[block_id] = name
            self._locks[name] = Lock()

            logger.info(f"Shared memory block '{name}' created (ID: {block_id}, Size: {nbytes} bytes).")
            return block_id
        except Exception as e:
            logger.error(f"Failed to create shared memory block '{name}': {e}")
            raise

    @Profiler.profile  
    def get_block(self, name: str) -> np.ndarray:
        """Returns a NumPy array referencing the shared memory block."""
        if name not in self._blocks:
            logger.error(f"Block '{name}' not found during get_block().")
            raise KeyError(f"Block '{name}' not found.")

        shm, shape, dtype, _ = self._blocks[name]
        logger.debug(f"Shared memory block '{name}' accessed.")
        return np.ndarray(shape, dtype=dtype, buffer=shm.buf)

    @Profiler.profile  
    def write(self, name: str, data: np.ndarray):
        """Write new data to an existing shared memory block."""
        if name not in self._blocks:
            logger.error(f"Block '{name}' not found during write().")
            raise KeyError(f"Block '{name}' not found.")

        shm, shape, dtype, _ = self._blocks[name]

        if data.shape != shape or data.dtype != dtype:
            logger.error(f"Incompatible shape or dtype for block '{name}'. Expected {shape}, got {data.shape}.")
            raise ValueError("Incompatible shape or dtype for shared memory block.")

        with self._locks[name]:
            np.copyto(np.ndarray(shape, dtype=dtype, buffer=shm.buf), data)
            logger.debug(f"Data written to shared memory block '{name}'.")

    @Profiler.profile  
    def read(self, name: str) -> np.ndarray:
        """Read and return a copy of the shared memory block data."""
        if name not in self._blocks:
            logger.error(f"Block '{name}' not found during read().")
            raise KeyError(f"Block '{name}' not found.")

        shm, shape, dtype, _ = self._blocks[name]
        with self._locks[name]:
            logger.debug(f"Data read from shared memory block '{name}'.")
            return np.ndarray(shape, dtype=dtype, buffer=shm.buf).copy()

    @Profiler.profile  
    def close_block(self, name: str):
        """Close a shared memory block but do not remove it."""
        if name in self._blocks:
            block_id = self._blocks[name][3]
            self._blocks[name][0].close()
            del self._blocks[name]
            del self._id_map[block_id]
            del self._locks[name]
            logger.info(f"Shared memory block '{name}' closed.")

    @Profiler.profile  
    def unlink_block(self, name: str):
        """Permanently remove a shared memory block from the OS."""
        if name in self._blocks:
            block_id = self._blocks[name][3]
            try:
                self._blocks[name][0].close()
                self._blocks[name][0].unlink()
                del self._blocks[name]
                del self._id_map[block_id]
                del self._locks[name]
                logger.info(f"Shared memory block '{name}' unlinked and deleted from the OS.")
            except Exception as e:
                logger.error(f"Failed to unlink block '{name}': {e}")

    @Profiler.profile  
    def close_all(self):
        """Close all shared memory blocks without deleting them."""
        for name in list(self._blocks.keys()):
            self.close_block(name)
        logger.info("All shared memory blocks closed.")

    @Profiler.profile  
    def unlink_all(self):
        """Close and permanently delete all shared memory blocks."""
        for name in list(self._blocks.keys()):
            self.unlink_block(name)
        logger.info("All shared memory blocks unlinked and deleted.")
