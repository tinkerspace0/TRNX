import numpy as np
from multiprocessing import shared_memory, Lock
import threading

class SharedMemoryPort:
    """
    Represents a shared memory block that can be attached to a Namespace.
    Automatically removes itself from its namespace when closed.
    """

    def __init__(self, name: str, shape: tuple, dtype=np.float64, namespace=None):
        """
        Initialize a shared memory port.

        Args:
            name (str): The unique name of the shared memory block.
            shape (tuple): Shape of the shared memory array.
            dtype (numpy.dtype): Data type of the array (default: float64).
            namespace (Namespace, optional): Reference to the parent namespace.
        """
        self.name = name
        self.shape = shape
        self.dtype = dtype
        self.namespace = namespace  # Store reference to parent namespace
        self.nbytes = np.prod(shape) * np.dtype(dtype).itemsize
        self.lock = threading.Lock()  # Ensure thread safety

        try:
            # Try attaching to an existing shared memory block
            self.shm = shared_memory.SharedMemory(name=self.name, create=False)
        except FileNotFoundError:
            # If it doesn't exist, create a new one
            self.shm = shared_memory.SharedMemory(name=self.name, create=True, size=self.nbytes)
            self._initialize_memory()

        self.array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
        self._new_data_available = False

    def _initialize_memory(self):
        """Zero out the shared memory when first created."""
        with self.lock:
            temp_array = np.ndarray(self.shape, dtype=self.dtype, buffer=self.shm.buf)
            temp_array.fill(0)

    def write(self, data: np.ndarray):
        """Write new data to the shared memory block."""
        if data.shape != self.shape or data.dtype != self.dtype:
            raise ValueError(f"Incompatible data shape {data.shape} or dtype {data.dtype}")

        with self.lock:
            np.copyto(self.array, data)
            self._new_data_available = True

    def read(self) -> np.ndarray:
        """Read the current data from the shared memory block."""
        with self.lock:
            self._new_data_available = False
            return self.array.copy()

    def new_data_available(self) -> bool:
        """Check if new data has been written since the last read."""
        return self._new_data_available

    def close(self):
        """Close the shared memory block and remove from namespace."""
        self.shm.close()
        if self.namespace:
            self.namespace._remove_shared_memory(self.name)

    def unlink(self):
        """Unlink (delete) the shared memory block from the system."""
        self.shm.unlink()
        if self.namespace:
            self.namespace._remove_shared_memory(self.name)
