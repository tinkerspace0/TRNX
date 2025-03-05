import numpy as np
from multiprocessing import shared_memory, Lock
import threading

from trenex.core.utils.identity import IDGenerator
from trenex.core.debug.profiler import Profiler

class SharedMemoryPort:
    """
    Represents a shared memory block.
    """

    @Profiler.profile
    def __init__(self, name: str, shape: tuple, dtype=np.float64):
        """
        Initialize a shared memory port.

        Args:
            name (str): The unique name of the shared memory block.
            shape (tuple): Shape of the shared memory array.
            dtype (numpy.dtype): Data type of the array (default: float64).
        """
        self.id = IDGenerator.generate_id()
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.nbytes = np.prod(shape) * np.dtype(dtype).itemsize
        self.lock = threading.Lock()  # Ensure thread safety

        try:
            # Try attaching to an existing shared memory block
            self.shm = shared_memory.SharedMemory(name=self.name, create=False)
        except (FileNotFoundError, ValueError):
            # If it doesn't exist, create a new one
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.nbytes)
            self._initialize_memory()

        self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)

    @Profiler.profile
    def _initialize_memory(self):
        """Zero out the shared memory when first created."""
        temp_array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
        temp_array.fill(0)

    @Profiler.profile
    def write(self, data: np.ndarray):
        """Write new data to the shared memory block."""
        if data.shape != self.shape or data.dtype != self.dtype:
            raise ValueError(f"Incompatible data shape {data.shape} or dtype {data.dtype}")

        with self.lock:
            np.copyto(self.array, data)

    @Profiler.profile
    def read(self) -> np.ndarray:
        """Read the current data from the shared memory block."""
        with self.lock:
            return self.array.copy()

    @Profiler.profile
    def close(self):
        """Close the shared memory block."""
        self.shm.close()

    @Profiler.profile
    def unlink(self):
        """Unlink (delete) the shared memory block from the system."""
        self.shm.unlink()
