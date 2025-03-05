from typing import Dict, Optional
from abc import abstractmethod

from trenex.core.memory.shared_memory_port import SharedMemoryPort
from trenex.core.base.plugin_base import Plugin

class DataProcessorPlugin(Plugin):
    """
    Base class for Data Processor Plugins.
    
    This plugin is intended for processing market data (e.g., calculating indicators,
    extracting features) and producing outputs that can be consumed by other parts of the system.
    """
    def __init__(self, config_file: Optional[str] = None):
        super().__init__(config_file)
        # Initialize inputs and outputs as empty dictionaries.
        self._inputs: Dict[str, SharedMemoryPort] = {}
        self._outputs: Dict[str, SharedMemoryPort] = {}
        # Optionally, initialize default configuration parameters here.
    
    def build(self) -> None:
        """
        Finalize plugin setup, such as loading configuration and creating shared memory ports.
        Concrete plugins should override this method if additional build steps are needed.
        """
        # Example: Create shared memory ports based on configuration.
        # For instance, if a plugin calculates RSI for periods [14, 21],
        # it might do something like:
        # self._outputs = {f"RSI_{period}": SharedMemoryPort(f"rsi_{period}", (1, 1)) for period in self._config.get("periods", [])}
        pass

    @property
    def inputs(self) -> Dict[str, SharedMemoryPort]:
        """
        Returns the dictionary of required input shared memory ports.
        """
        return self._inputs

    @property
    def outputs(self) -> Dict[str, SharedMemoryPort]:
        """
        Returns the dictionary of provided output shared memory ports.
        """
        return self._outputs

    @abstractmethod
    def process(self) -> None:
        """
        Execute the plugin's processing logic.
        
        The implementing plugin should:
          - Read data from the input SharedMemoryPort(s) via self._inputs.
          - Perform its processing (e.g., compute an indicator, extract features).
          - Write the result(s) to the output SharedMemoryPort(s) via self._outputs.
        """
        raise NotImplementedError("Process method not implemented.")
