# shared_memory.py

import numpy as np
from multiprocessing import shared_memory, Lock
from core.identity import IDGenerator
import threading

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
        return cls._instance

    def _initialize(self):
        """Initialize internal storage for shared memory blocks."""
        self._blocks = {}  # Stores name -> (SharedMemory instance, shape, dtype, block_id)
        self._id_map = {}  # Stores block_id -> name
        self._locks = {}   # Stores name -> Lock

    def create_block(self, name: str, data: np.ndarray) -> str:
        """
        Create a new shared memory block with a given name and return its block ID.
        """
        if name in self._blocks:
            raise ValueError(f"Block '{name}' already exists.")

        block_id = IDGenerator.generate_id()
        shape, dtype = data.shape, data.dtype
        nbytes = np.prod(shape) * dtype.itemsize

        shm = shared_memory.SharedMemory(name=block_id, create=True, size=nbytes)
        array = np.ndarray(shape, dtype=dtype, buffer=shm.buf)
        np.copyto(array, data)

        # Store under the given name
        self._blocks[name] = (shm, shape, dtype, block_id)
        self._id_map[block_id] = name
        self._locks[name] = Lock()

        return block_id  # Returns ID for external reference

    def get_block(self, name: str) -> np.ndarray:
        """
        Returns a NumPy array referencing the shared memory block.
        """
        if name not in self._blocks:
            raise KeyError(f"Block '{name}' not found.")

        shm, shape, dtype, _ = self._blocks[name]
        return np.ndarray(shape, dtype=dtype, buffer=shm.buf)

    def get_block_by_id(self, block_id: str) -> np.ndarray:
        """
        Retrieve a shared memory block using its block ID.
        """
        if block_id not in self._id_map:
            raise KeyError(f"Block ID '{block_id}' not found.")

        name = self._id_map[block_id]
        return self.get_block(name)

    def write(self, name: str, data: np.ndarray):
        """
        Write new data to an existing shared memory block.
        """
        if name not in self._blocks:
            raise KeyError(f"Block '{name}' not found.")

        shm, shape, dtype, _ = self._blocks[name]

        if data.shape != shape or data.dtype != dtype:
            raise ValueError("Incompatible shape or dtype for shared memory block.")

        with self._locks[name]:
            np.copyto(np.ndarray(shape, dtype=dtype, buffer=shm.buf), data)

    def read(self, name: str) -> np.ndarray:
        """
        Read and return a copy of the shared memory block data.
        """
        if name not in self._blocks:
            raise KeyError(f"Block '{name}' not found.")

        shm, shape, dtype, _ = self._blocks[name]
        with self._locks[name]:
            return np.ndarray(shape, dtype=dtype, buffer=shm.buf).copy()

    def close_block(self, name: str):
        """
        Close a shared memory block but do not remove it.
        """
        if name in self._blocks:
            block_id = self._blocks[name][3]
            self._blocks[name][0].close()
            del self._blocks[name]
            del self._id_map[block_id]
            del self._locks[name]

    def unlink_block(self, name: str):
        """
        Permanently remove a shared memory block from the OS.
        """
        if name in self._blocks:
            block_id = self._blocks[name][3]
            self._blocks[name][0].close()
            self._blocks[name][0].unlink()
            del self._blocks[name]
            del self._id_map[block_id]
            del self._locks[name]

    def close_all(self):
        """
        Close all shared memory blocks without deleting them.
        """
        for name in list(self._blocks.keys()):
            self.close_block(name)

    def unlink_all(self):
        """
        Close and permanently delete all shared memory blocks.
        """
        for name in list(self._blocks.keys()):
            self.unlink_block(name)

    def __getattr__(self, name: str):
        """
        Enable dot-access retrieval of shared memory blocks.
        Example: `data = manager.some_block`
        """
        if name in self._blocks:
            return self.read(name)
        raise AttributeError(f"No shared memory block named '{name}'")

    def __setattr__(self, name: str, value):
        """
        Enable dot-access creation of shared memory blocks.
        Example: `manager.some_block = np.array([...])`
        """
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        if not isinstance(value, np.ndarray):
            raise ValueError(f"Assigned value must be a NumPy array. Got {type(value)} instead.")

        # Create or overwrite block
        if name in self._blocks:
            self.write(name, value)
        else:
            self.create_block(name, value)

    def __delattr__(self, name: str):
        """
        Enable `del manager.some_block` to remove shared memory.
        """
        if name in self._blocks:
            self.unlink_block(name)
        else:
            raise AttributeError(f"No shared memory block named '{name}' to delete.")
