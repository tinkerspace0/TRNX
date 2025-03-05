from typing import List, Dict, Tuple

from trenex.core.debug.logger import logger
from trenex.core.base import Plugin
from trenex.core.memory import SharedMemoryPort

class Trenex:
    """
    Main bot class that holds and executes plugins.
    The build process determines the execution order based on plugin dependencies:
    a plugin that uses the output of another plugin will be executed after the provider.
    """
    def __init__(self) -> None:
        # List of all attached plugins.
        self.plugins: List[Plugin] = []
        # Execution order computed based on dependency graph.
        self.execution_order: List[Plugin] = []
        # Mapping from an output plugin to its outputs and connected input plugins.
        # Structure: { output_plugin: { output_name: List of (input_plugin, input_name) } }
        self._plugin_connections: Dict[Plugin, Dict[str, List[Tuple[Plugin, str]]]] = {}

    def attach_plugin(self, plugin: Plugin) -> None:
        """
        Attach a plugin to the bot.

        Args:
            plugin (Plugin): The plugin instance to attach.
        """
        self.plugins.append(plugin)
        logger.info(f"Attached plugin: {plugin.__class__.__name__}")

    def detach_plugin(self, plugin: Plugin) -> None:
        """
        Detach a plugin from the bot.

        Args:
            plugin (Plugin): The plugin instance to detach.
        """
        if plugin in self.plugins:
            self.plugins.remove(plugin)
            logger.info(f"Detached plugin: {plugin.__class__.__name__}")
        else:
            logger.warning(f"Plugin {plugin.__class__.__name__} not found in the list of attached plugins.")

    def connect_plugin_output_to_input(self, output_plugin: Plugin, output_name: str, input_plugin: Plugin, input_name: str) -> None:
        """
        Connect the output of one plugin to the input of another.

        Args:
            output_plugin (Plugin): The plugin providing the output.
            output_name (str): The name of the output port.
            input_plugin (Plugin): The plugin receiving the input.
            input_name (str): The name of the input port.
        """
        if output_plugin not in self._plugin_connections:
            self._plugin_connections[output_plugin] = {}
        if output_name not in self._plugin_connections[output_plugin]:
            self._plugin_connections[output_plugin][output_name] = []
        self._plugin_connections[output_plugin][output_name].append((input_plugin, input_name))
        logger.info(
            f"Connected output {output_name} of plugin {output_plugin.__class__.__name__} "
            f"to input {input_name} of plugin {input_plugin.__class__.__name__}"
        )

    def _compute_execution_order(self) -> None:
        """
        Compute the execution order of plugins based on the dependency graph derived from plugin connections.
        A plugin that uses the output of another plugin will be executed after the plugin providing the output.
        
        Raises:
            RuntimeError: If a cycle is detected in plugin dependencies.
        """
        # Initialize dependency graph and in-degree counts for each plugin.
        dependency_graph = {plugin: set() for plugin in self.plugins}
        in_degree = {plugin: 0 for plugin in self.plugins}

        # For each connection, add an edge from the output plugin to the input plugin.
        for output_plugin, outputs in self._plugin_connections.items():
            for output_name, input_connections in outputs.items():
                for input_plugin, input_name in input_connections:
                    if input_plugin not in dependency_graph[output_plugin]:
                        dependency_graph[output_plugin].add(input_plugin)
                        in_degree[input_plugin] += 1

        # Kahn's algorithm for topological sorting.
        sorted_plugins = []
        # Start with all plugins that have no incoming dependencies.
        queue = [plugin for plugin in self.plugins if in_degree[plugin] == 0]

        while queue:
            current = queue.pop(0)
            sorted_plugins.append(current)
            for dependent in dependency_graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(sorted_plugins) != len(self.plugins):
            raise RuntimeError("Cycle detected in plugin dependencies; cannot compute execution order.")

        self.execution_order = sorted_plugins

    def build(self) -> None:
        """
        Build the bot by finalizing each plugin's configuration.
        This process:
            1. Creates shared memory ports for each output based on defined connections.
            2. Sets up the connections between plugin outputs and inputs.
            3. Computes the execution order based on plugin dependencies.
            4. Invokes each plugin's build method.
        """
        # Set up shared memory ports and connect plugin inputs/outputs.
        for output_plugin, output_connections in self._plugin_connections.items():
            for output_name, input_connections in output_connections.items():
                # Create a unique port name.
                port_name = f"{output_plugin.__class__.__name__}_{output_name}"
                shape = output_plugin._provided_outputs[output_name][0]
                dtype = output_plugin._provided_outputs[output_name][1]
                # Create the shared memory port instance.
                port = SharedMemoryPort(port_name, shape, dtype)
                logger.info(f"Created shared memory port {port_name} with shape {shape} and dtype {dtype}")
                output_plugin.set_output_port(output_name, port)
                logger.info(f"Set output port {output_name} of plugin {output_plugin.__class__.__name__} to shared memory port {port_name}")
                for input_plugin, input_name in input_connections:
                    input_plugin.set_input_port(input_name, port)
                    logger.info(f"Set input port {input_name} of plugin {input_plugin.__class__.__name__} to shared memory port {port_name}")

        # Compute execution order based on plugin dependencies.
        self._compute_execution_order()
        logger.info("Computed execution order based on plugin dependencies:")
        for idx, plugin in enumerate(self.execution_order):
            logger.info(f"Execution order {idx + 1}: {plugin.__class__.__name__}")

        # Build each plugin in the computed execution order.
        for plugin in self.execution_order:
            plugin.build()

        logger.info("Trenex build complete.")

    def run(self) -> None:
        """
        Execute all plugins in the dependency-determined execution order.
        After build, plugins are executed in an order that respects their data dependencies.
        """
        for plugin in self.execution_order:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
