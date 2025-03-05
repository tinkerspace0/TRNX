from core.shared_memory import SharedMemoryPort
from core.debug.logger import logger

class Node:
    def __init__(self, name: str, node_type: str):
        """
        Args:
            name (str): Name of the node.
            node_type (str): Type of node (Exchange, DataProcessor, Strategy, Agent).
        """
        self._name = name
        self._type = node_type
        self._inputs = {}  # {input_name: SharedMemoryPort()}
        self._outputs = {}  # {output_name: SharedMemoryPort()}
        self._plugin = None

    def attach_plugin(self, plugin):
        """Attaches a plugin to the node and initializes inputs."""
        self._plugin = plugin
        self._inputs = {key: None for key in plugin.required_inputs()}  # Define input slots
        self._outputs = {key: SharedMemoryPort() for key in plugin.provided_outputs()}  # Define outputs

    def connect(self, input_name: str, node, output_name: str):
        """Connects an input of this node to an output of another node."""
        if input_name not in self._inputs:
            raise ValueError(f"Input '{input_name}' not found in node '{self._name}'")
        if output_name not in node._outputs:
            raise ValueError(f"Output '{output_name}' not found in node '{node._name}'")

        self._inputs[input_name] = node._outputs[output_name]  # Link input to output
        logger.info(f"Connected {node._name}.{output_name} → {self._name}.{input_name}")

    def build(self):
        """Finalizes the setup and injects SharedMemoryPort into the plugin."""
        if not self._plugin:
            raise ValueError(f"Node '{self._name}' has no attached plugin.")

        # Assign shared memory ports to plugin inputs and outputs
        for input_name in self._inputs:
            if self._inputs[input_name]:
                self._plugin.set_input_port(input_name, self._inputs[input_name])

        for output_name in self._outputs:
            self._plugin.set_output_port(output_name, self._outputs[output_name])

        logger.info(f"Node '{self._name}' built. Plugin can now run independently.")
