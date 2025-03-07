# core/plugin/plugin_base.py
from abc import ABC, abstractmethod
from typing import Dict, Tuple
import numpy as np
from core.memory.shared_memory_port import SharedMemoryPort
from core.utils.identity import IDGenerator

class Plugin(ABC):
    """
    Base class for all plugins.
    Provides interfaces for defining required inputs, provided outputs, and processing logic.
    """
    def __init__(self):
        self.id = IDGenerator.generate_id(self)
        self._required_inputs: Dict[str, Tuple[Tuple[int, ...], np.dtype]] = {}
        self._provided_outputs: Dict[str, Tuple[Tuple[int, ...], np.dtype]] = {}
        self._inputs: Dict[str, SharedMemoryPort] = {}
        self._outputs: Dict[str, SharedMemoryPort] = {}

    def required_inputs_ports(self) -> Dict[str, Tuple[Tuple[int, ...], np.dtype]]:
        self._define_inputs()
        return self._required_inputs

    def provided_outputs_ports(self) -> Dict[str, Tuple[Tuple[int, ...], np.dtype]]:
        self._define_outputs()
        return self._provided_outputs

    def set_input_port(self, input_name: str, shm_port: SharedMemoryPort) -> None:
        if input_name in self._required_inputs:
            self._inputs[input_name] = shm_port
        else:
            raise ValueError(f"Input {input_name} not defined.")

    def set_output_port(self, output_name: str, shm_port: SharedMemoryPort) -> None:
        if output_name in self._provided_outputs:
            self._outputs[output_name] = shm_port
        else:
            raise ValueError(f"Output {output_name} not defined.")

    def verify(self) -> None:
        """
        Verify that all required plugin inputs are set.
        """
        if not all([port in self._inputs for port in self._required_inputs]):
            raise ValueError("Not all required inputs set.")

    def _write_output(self, output_name: str, data: np.ndarray) -> None:
        if output_name in self._outputs and self._outputs[output_name] is not None:
            self._outputs[output_name].write(data)
        else:
            raise ValueError(f"Output {output_name} not defined.")
        
    @abstractmethod
    def process(self) -> None:
        """
        Execute the plugin's processing logic.
        """
        raise NotImplementedError("Process not implemented.")

    @abstractmethod
    def _define_inputs(self) -> None:
        """
        Define required input ports.
        """
        pass

    @abstractmethod
    def _define_outputs(self) -> None:
        """
        Define provided output ports.
        """
        pass