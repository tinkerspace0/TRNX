# core/node/node_base.py
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import numpy as np

from core.node.node_io import NodeIO
from core.node.node_param import Parameters
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
        self._static_params = Parameters(self)  # Static Parameters for the node.
        self._dynamic_params = Parameters(self) # Dynamic Parameters for the node.
        self._io_in = NodeIO(self, NodeIO.IOType.INPUT)     # Input/Output interface for the node inputs.
        self._io_out = NodeIO(self, NodeIO.IOType.OUTPUT)   # Input/Output interface for the node outputs.

    def get_static_params(self) :
        """
        Get the static/(runtime immutable) parameters of the node.
        """
        return self._static_params
    
    def get_dynamic_params(self) :
        """
        Get the dynamic/(runtime mutable) parameters of the node.
        """
        return self._dynamic_params
    
    def get_in_io(self) -> NodeIO:
        """
        Get the input/output interface for the node inputs.
        """
        return self._io_in
    
    def get_out_io(self) -> NodeIO:
        """
        Get the input/output interface for the node outputs.
        """
        return self._io_out
    
    def get_io(self) -> Tuple[NodeIO, NodeIO]:
        """
        Get the input/output interfaces for the node inputs and outputs.
        """
        return self._io_in, self._io_out
    
    def verify(self) -> None:
        """
        Verify the node configuration.
        This includes checking the static and dynamic parameters, and the input/output definitions.
        """
        # TODO - Check static and dynamic parameters for validity.
        # TODO - Check the input and output NodeIO for validity.
        pass

    @abstractmethod    
    def update_io(self) -> None:
        """
        Update the input and output definitions based on the current static parameters.
        Must be implemented in derived NodeConfig classes.
        """
        raise NotImplementedError("update_io() must be implemented in derived NodeConfig classes.")


    @abstractmethod
    def process(self) -> None:
        """Execute the node's processing logic."""
        raise NotImplementedError("Process method not implemented.")