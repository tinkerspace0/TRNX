# core/node/node_base.py
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import numpy as np

from core.node.node_config import NodeConfig
from core.memory.shared_memory_port import SharedMemoryPort
from core.utils.identity import IDGenerator
from core.debug.logger import gl_logger

class Node(ABC):
    """
    Base class for all nodes (ie Components).
    Each node has a configuration (NodeConfig) that defines its inputs, outputs, and parameters.
    """
    def __init__(self, name: str = None):
        self.id = IDGenerator.generate_id(self)
        self.name = name if name else f"Node_{self.id}"
        self.config = NodeConfig()  # Derived nodes should update this configuration.
        self._inputs: Dict[str, SharedMemoryPort] = {}      # Actual shared memory ports for inputs.
        self._outputs: Dict[str, SharedMemoryPort] = {}     # Actual shared memory ports for outputs.

    def set_input_port(self, port_name: str, shm_port: SharedMemoryPort) -> None:
        if port_name in self.config.inputs:
            self._inputs[port_name] = shm_port
        else:
            raise ValueError(f"Input port '{port_name}' is not defined in the node configuration.")

    def set_output_port(self, port_name: str, shm_port: SharedMemoryPort) -> None:
        if port_name in self.config.outputs:
            self._outputs[port_name] = shm_port
        else:
            raise ValueError(f"Output port '{port_name}' is not defined in the node configuration.")

    def verify(self) -> None:
        """
        Verify that all required plugin inputs are set.
        """
        # TODO - Check from config for the required pors
        # TODO - Add a check for the shape of the data.
        # TODO - Add a check for the dtype of the data.
        if not all([port in self._inputs for port in self._required_inputs]):
            raise ValueError("Not all required inputs set.")

    def _write_output(self, port_name: str, data):
        """
        Write data to an output port only if it is set.
        Converts data to a NumPy array with the expected dtype.
        """
        # TODO - Check if implementation is correct.
        # TODO - Check if the data is of the correct shape.
        # TODO - Check if the data is of the correct dtype.
        # TODO - Check if the data is of the correct size.
        if port_name in self._outputs and self._outputs[port_name] is not None:
            if not isinstance(data, np.ndarray):
                expected_dtype = self.config.outputs[port_name][1]
                data = np.array(data, dtype=expected_dtype)
            self._outputs[port_name].write(data)
            gl_logger.info(f"Data written to output port '{port_name}'.")
        else:
            gl_logger.info(f"Output port '{port_name}' not set. Data not written.")

    @abstractmethod
    def process(self) -> None:
        """Execute the node's processing logic."""
        raise NotImplementedError("Process method not implemented.")