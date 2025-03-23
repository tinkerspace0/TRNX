from enum import Enum
from typing import Dict, Tuple, Any
from dataclasses import dataclass

from core.memory import SharedMemoryPort
from core.node.node_base import Node
from core.debug.logger import gl_logger

class IO:
    """
    Represents an individual Input/Output (IO) channel for a node.

    Attributes:
        name (str): The name of the IO channel.
        dtype (type): The data type for this IO.
        shape (tuple): The shape of the data for this IO.
        shm (SharedMemoryPort): The associated shared memory port (if initialized).
    """
    def __init__(self, name: str, dtype: type = float, shape: Tuple[int, ...] = None) -> None:
        self.name: str = name
        self.dtype: type = dtype
        self.shape: Tuple[int, ...] = shape
        self.shm: SharedMemoryPort = None
        gl_logger.debug(f"Initialized IO: {self}")

    def set_shm(self, shm: SharedMemoryPort) -> None:
        """
        Set the shared memory port for this IO.

        Args:
            shm (SharedMemoryPort): The shared memory port to associate with this IO.
        """
        self.shm = shm
        gl_logger.info(f"Set shared memory for IO '{self.name}'.")

    def get_shm(self) -> SharedMemoryPort:
        """
        Get the shared memory port associated with this IO.

        Returns:
            SharedMemoryPort: The associated shared memory port.
        """
        return self.shm

    def initialize_shm(self) -> None:
        """
        Initialize the shared memory port if it hasn't been initialized.
        """
        if self.shm is None:
            self.shm = SharedMemoryPort(name=self.name, dtype=self.dtype, shape=self.shape)
            gl_logger.info(f"Initialized shared memory for IO '{self.name}'.")

    def write(self, data: Any) -> None:
        """
        Write data to the associated shared memory port.

        Args:
            data: The data to write.
        """
        if self.shm:
            self.shm.write(data)
            gl_logger.debug(f"Data written to IO '{self.name}'.")
        else:
            gl_logger.error(f"Shared memory for IO '{self.name}' is not initialized.")
            raise RuntimeError(f"Shared memory for IO '{self.name}' is not initialized.")

    def read(self) -> Any:
        """
        Read data from the associated shared memory port.

        Returns:
            The data read from the shared memory port, or None if not set.
        """
        if self.shm:
            gl_logger.debug(f"Data read from IO '{self.name}'.")
            return self.shm.read()
        gl_logger.warning(f"Attempted to read from uninitialized IO '{self.name}'.")
        return None

    def __repr__(self) -> str:
        return f"IO(name={self.name}, shape={self.shape}, dtype={self.dtype.__name__})"


class NodeIO:
    """
    Manages multiple IO instances for a node.
    
    IO instances are stored internally and exposed via dot notation.
    
    Attributes:
        _node (Node): The parent node this IO belongs to.
        _io_type (IOType): Specifies whether these IOs are inputs or outputs.
        _ios (Dict[str, IO]): Dictionary mapping IO names to IO instances.
    """

    class IOType(Enum):
        INPUT = "input"
        OUTPUT = "output"

    def __init__(self, parent_node: Node, io_type: "NodeIO.IOType") -> None:
        self._node = parent_node
        self._io_type = io_type
        # Internal dictionary to hold IO instances.
        self.__dict__["_ios"]: Dict[str, IO] = {}   # type: ignore
        gl_logger.debug(f"Initialized {self._io_type.value} IO for node '{self._node.name}'.")

    def create_io(self, name: str, dtype: type = float, shape: Tuple[int, ...] = None) -> None:
        """
        Create an IO object with the given name and attach it as an attribute.

        Args:
            name (str): The name of the IO.
            dtype (type): The data type for the IO (default is float).
            shape (tuple): The expected shape of the IO data.

        Raises:
            ValueError: If an IO with the given name already exists.
        """
        if name in self._ios:
            gl_logger.error(f"IO with name '{name}' already exists.")
            raise ValueError(f"IO with name '{name}' already exists.")
        io = IO(name=name, dtype=dtype, shape=shape)
        self._ios[name] = io
        super().__setattr__(name, io)
        gl_logger.info(f"Created IO '{name}' with dtype {dtype.__name__} and shape {shape}.")

    def get(self, name: str) -> IO:
        """
        Retrieve an IO object by its name.

        Args:
            name (str): The name of the IO.

        Returns:
            IO: The IO object with the specified name.

        Raises:
            KeyError: If no IO with the given name exists.
        """
        if name in self._ios:
            gl_logger.debug(f"Retrieved IO '{name}'.")
            return self._ios[name]
        gl_logger.error(f"IO with name '{name}' not found.")
        raise KeyError(f"IO with name '{name}' not found.")

    @property
    def all(self) -> Dict[str, IO]:
        """
        Get all IO objects as a dictionary.

        Returns:
            Dict[str, IO]: A dictionary mapping IO names to IO objects.
        """
        return self._ios

    def __getattr__(self, name: str) -> IO:
        """
        Provide dot notation access to IO objects stored in _ios.

        Args:
            name (str): The name of the IO.

        Returns:
            IO: The IO object if it exists.

        Raises:
            AttributeError: If no IO with the given name exists.
        """
        if name in self._ios:
            return self._ios[name]
        gl_logger.error(f"No IO named '{name}' found.")
        raise AttributeError(f"No IO named '{name}' found.")

    def __repr__(self) -> str:
        return f"{self._io_type.name.capitalize()}IO({list(self._ios.keys())})"

@dataclass
class IOConnection:
    output_node: Node
    output_port: str
    input_node: Node
    input_port: str