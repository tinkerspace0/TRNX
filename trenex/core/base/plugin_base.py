from abc import ABC, abstractmethod
from typing import Dict, Tuple, Optional
import numpy as np

from trenex.core.memory import SharedMemoryPort
from trenex.core.utils import IDGenerator

class Plugin(ABC):
    """
    Base class for all plugins.
    Provides an interface for defining required inputs, provided outputs,
    and processing logic.
    """

    def __init__(self):
        # Generate a unique ID for the plugin instance.
        self.id = IDGenerator.generate_id(self)
        # Mapping from input name to (shape, dtype).
        self._required_inputs: Dict[str, Tuple[Tuple[int, ...], np.dtype]] = {}
        # Mapping from output name to (shape, dtype).
        self._provided_outputs: Dict[str, Tuple[Tuple[int, ...], np.dtype]] = {}
        # These dictionaries will hold the actual SharedMemoryPort objects after build().
        self._inputs: Dict[str, SharedMemoryPort] = {}
        self._outputs: Dict[str, SharedMemoryPort] = {}

    def required_inputs_ports(self) -> Dict[str, Tuple[Tuple[int, ...], np.dtype]]:
        """
        Define and return a dictionary of required input ports for the plugin.

        Returns:
            Dict[str, Tuple[Tuple[int, ...], np.dtype]]: Mapping of input names to their (shape, dtype).
        """
        self._define_inputs()
        return self._required_inputs

    def provided_outputs_ports(self) -> Dict[str, Tuple[Tuple[int, ...], np.dtype]]:
        """
        Define and return a dictionary of provided output ports for the plugin.

        Returns:
            Dict[str, Tuple[Tuple[int, ...], np.dtype]]: Mapping of output names to their (shape, dtype).
        """
        self._define_outputs()
        return self._provided_outputs  # Fixed: now returns _provided_outputs.

    @abstractmethod
    def _define_inputs(self) -> None:
        """
        Define the required inputs for the plugin.
        Implementations should set self._required_inputs to a dict with keys as input names and values as (shape, dtype).
        """
        pass

    @abstractmethod
    def _define_outputs(self) -> None:
        """
        Define the provided outputs for the plugin.
        Implementations should set self._provided_outputs to a dict with keys as output names and values as (shape, dtype).
        """
        pass

    def set_input_port(self, input_name: str, shm_port: SharedMemoryPort) -> None:
        """
        Set the shared memory port for a specified input.

        Args:
            input_name (str): Name of the input port.
            shm_port (SharedMemoryPort): Shared memory port to associate with the input.
        
        Raises:
            ValueError: If the input name is not defined in the required inputs.
        """
        if input_name in self._required_inputs.keys():
            self._inputs[input_name] = shm_port
        else:
            raise ValueError(f"Input name {input_name} not found in required inputs.")

    def set_output_port(self, output_name: str, shm_port: SharedMemoryPort) -> None:
        """
        Set the shared memory port for a specified output.

        Args:
            output_name (str): Name of the output port.
            shm_port (SharedMemoryPort): Shared memory port to associate with the output.
        
        Raises:
            ValueError: If the output name is not defined in the provided outputs.
        """
        if output_name in self._provided_outputs.keys():
            self._outputs[output_name] = shm_port
        else:
            raise ValueError(f"Output name {output_name} not found in provided outputs.")

    def build(self) -> None:
        """
        Build the plugin.
        This method can be overridden by plugins to perform any initialization after ports are set.
        """
        pass

    @abstractmethod
    def process(self) -> None:
        """
        Execute the plugin's processing logic.
        Implementations should override this method.
        """
        raise NotImplementedError("Process method not implemented.")
