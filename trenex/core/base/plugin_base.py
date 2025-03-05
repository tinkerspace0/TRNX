from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from trenex.core.memory.shared_memory_port import SharedMemoryPort

class Plugin(ABC):
    """
    Base class for plugins. Each plugin should:
      - Define required inputs (e.g., data from shared memory).
      - Define outputs (e.g., indicators, signals).
      - Provide a process() method.
      - Declare its execution priority (lower numbers execute first).
    """

    def __init__(self, config_file: Optional[str] = None):
        self.config_file: Optional[str] = config_file
        self._inputs: Dict[str, SharedMemoryPort] = {}  # Required input names
        self._outputs: Dict[str, SharedMemoryPort] = {}  # Provided output names
        self._dependent_plugins: List["Plugin"] = []  # Plugins that must run first
        self.priority: Optional[int] = None  # Execution priority (lower executes first)

    def required_inputs(self) -> Dict[str, SharedMemoryPort]:
        """
        Return a dictionary of required input names.
        """
        return self._inputs

    def provided_outputs(self) -> Dict[str, SharedMemoryPort]:
        """
        Return a dictionary of provided output names.
        """
        return self._outputs

    def _define_priority(self) -> int:
        """
        Set priority dynamically based on dependent plugins.
        """
        if self.priority is None:
            if len(self._dependent_plugins) == 0:
                self.priority = 1  # Default priority if no dependencies exist
            else:
                # Compute priority based on dependencies
                max_dep_priority = max(plugin._define_priority() for plugin in self._dependent_plugins)
                self.priority = max_dep_priority + 1

        return self.priority

    def add_dependency(self, plugin: "Plugin") -> None:
        """
        Add a plugin dependency.
        """
        if plugin not in self._dependent_plugins:
            self._dependent_plugins.append(plugin)
            self.priority = None  # Reset priority so it gets recalculated

    def build(self) -> None:
        """
        Finalize plugin setup (e.g., load configuration, create shared memory ports).
        """
        pass

    @abstractmethod
    def process(self) -> None:
        """
        Execute the plugin's processing logic.
        """
        raise NotImplementedError("Process method not implemented.")
