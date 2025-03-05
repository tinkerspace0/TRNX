import json
import importlib
from core.shared_memory import SharedMemoryPort
from core.debug.logger import logger

class NodeManager:
    """Manages node setup, serialization, and execution."""

    CONFIG_PATH = "configs/node_setup.json"

    def __init__(self):
        self.nodes = {}
        self.execution_order = []

    def load_config(self):
        """Loads node configuration from JSON."""
        try:
            with open(self.CONFIG_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load node setup config: {e}")
            return {}

    def save_config(self):
        """Saves current node setup to JSON."""
        try:
            with open(self.CONFIG_PATH, "w") as f:
                json.dump({name: node.serialize() for name, node in self.nodes.items()}, f, indent=4)
            logger.info("Node setup saved successfully.")
        except Exception as e:
            logger.error(f"Failed to save node setup: {e}")

    def initialize_nodes(self):
        """Creates nodes dynamically from config."""
        config = self.load_config()

        for node_name, node_data in config.items():
            module_path = f"modules.node_system.{node_data['type'].lower()}"
            try:
                module = importlib.import_module(module_path)
                node_class = getattr(module, node_data["type"])
                node_instance = node_class()
                self.nodes[node_name] = node_instance

                # Load plugin and assign inputs
                if "plugin" in node_data:
                    plugin_module = importlib.import_module(node_data["plugin"]["module"])
                    plugin_class = getattr(plugin_module, node_data["plugin"]["class"])
                    plugin_instance = plugin_class()
                    node_instance.attach_plugin(plugin_instance)

                if "inputs" in node_data:
                    for input_name, block_id in node_data["inputs"].items():
                        node_instance.set_input(input_name, SharedMemoryPort(block_id))

                self.execution_order.append(node_name)

                logger.info(f"Initialized node: {node_name} ({node_data['type']})")

            except Exception as e:
                logger.error(f"Failed to initialize node {node_name}: {e}")

    def modify_connection(self, node_name, input_name, target_node, output_name):
        """Dynamically modifies node connections."""
        if node_name not in self.nodes or target_node not in self.nodes:
            raise ValueError(f"Invalid nodes specified: {node_name} or {target_node} not found")

        self.nodes[node_name].connect(input_name, self.nodes[target_node], output_name)
        logger.info(f"Modified connection: {target_node}.{output_name} → {node_name}.{input_name}")

    def build(self):
        """Finalizes setup and makes plugins independent."""
        for node_name in self.execution_order:
            self.nodes[node_name].build()
        self.save_config()
        logger.info("Node system finalized. Plugins are now independent.")

    def execute(self):
        """Executes nodes after setup."""
        for node_name in self.execution_order:
            self.nodes[node_name].execute()
            logger.info(f"Executed node: {node_name}")
