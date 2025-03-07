# trenex.py
import os
from core.debug.logger import logger
from core.memory.shared_memory_port import SharedMemoryPort
from core.plugin.plugin_base import Plugin
from core.plugin.plugin_factory import create_template, package_plugin
from core.plugin.plugin_loader import load_plugin
from trenex.trnx import TRNX

class Trenex:
    """
    Builder for TRNX trading bots.
    
    Use Trenex to create a new TRNX instance, load plugins from file,
    connect plugin outputs/inputs, compute the correct execution order, 
    and build the final TRNX bot.
    """
    def __init__(self):
        self._trnxs = {}  # Dict[str, TRNX]
        self._active_trnx = None
        # For each TRNX, store loaded plugins: {plugin_name: (plugin_instance, plugin_filepath)}
        self._loaded_plugins = {}  
        # For each TRNX, store connection mappings:
        # {output_plugin: {output_port: [(input_plugin, input_port), ...]}}
        self._plugin_connections = {}  
        self.execution_order = []  # Execution order (list of plugin names)

    def start_new_trnx(self, name: str):
        if name in self._trnxs:
            raise ValueError(f"TRNX with name {name} already exists.")
        new_trnx = TRNX(name)
        self._trnxs[name] = new_trnx
        self._loaded_plugins[name] = {}
        self._plugin_connections[name] = {}
        self._active_trnx = new_trnx
        logger.info(f"Started new TRNX: {name}")

    def set_active_trnx(self, name: str):
        if name not in self._trnxs:
            raise ValueError(f"TRNX with name {name} does not exist.")
        self._active_trnx = self._trnxs[name]
        logger.info(f"Set active TRNX: {name}")

    def load_plugin(self, plugin_filepath: str):
        if self._active_trnx is None:
            raise ValueError("No active TRNX. Please start or set an active TRNX first.")
        plugin_instance = load_plugin(plugin_filepath)
        plugin_name = plugin_instance.__class__.__name__
        trnx_name = self._active_trnx._name
        plugin_instance._define_outputs()
        plugin_instance._define_inputs()
        self._loaded_plugins[trnx_name][plugin_name] = (plugin_instance, plugin_filepath)
        self._active_trnx._plugins.append(plugin_instance)
        logger.info(f"Loaded plugin {plugin_name} into TRNX {trnx_name}")

    def unload_plugin(self, plugin_name: str):
        if self._active_trnx is None:
            raise ValueError("No active TRNX.")
        trnx_name = self._active_trnx.name
        if plugin_name not in self._loaded_plugins[trnx_name]:
            raise ValueError(f"Plugin {plugin_name} not found in active TRNX.")
        plugin_instance, _ = self._loaded_plugins[trnx_name].pop(plugin_name)
        self._active_trnx.plugins.remove(plugin_instance)
        logger.info(f"Unloaded plugin {plugin_name} from TRNX {trnx_name}")

    def connect_plugin_output_to_input(self, output_plugin: str, output_port: str, input_plugin: str, input_port: str):
        if self._active_trnx is None:
            raise ValueError("No active TRNX.")
        trnx_name = self._active_trnx._name
        if output_plugin not in self._loaded_plugins[trnx_name]:
            raise ValueError(f"Output plugin {output_plugin} not loaded.")
        if input_plugin not in self._loaded_plugins[trnx_name]:
            raise ValueError(f"Input plugin {input_plugin} not loaded.")
        if output_plugin not in self._plugin_connections[trnx_name]:
            self._plugin_connections[trnx_name][output_plugin] = {}
        if output_port not in self._plugin_connections[trnx_name][output_plugin]:
            self._plugin_connections[trnx_name][output_plugin][output_port] = []
        self._plugin_connections[trnx_name][output_plugin][output_port].append((input_plugin, input_port))
        logger.info(f"Connected {output_plugin}:{output_port} -> {input_plugin}:{input_port}")

    def _compute_execution_order(self):
        """
        Compute the plugin execution order via topological sort.
        An edge from A to B indicates that B depends on A.
        """
        trnx_name = self._active_trnx._name
        plugins = self._loaded_plugins[trnx_name]
        # Initialize graph
        dependency_graph = {p: set() for p in plugins.keys()}
        in_degree = {p: 0 for p in plugins.keys()}

        # Build graph from connection mappings
        for out_plugin, ports in self._plugin_connections[trnx_name].items():
            for out_port, connections in ports.items():
                for in_plugin, in_port in connections:
                    if in_plugin not in dependency_graph[out_plugin]:
                        dependency_graph[out_plugin].add(in_plugin)
                        in_degree[in_plugin] += 1

        # Kahn's algorithm for topological sorting
        sorted_plugins = []
        queue = [p for p in plugins.keys() if in_degree[p] == 0]
        while queue:
            current = queue.pop(0)
            sorted_plugins.append(current)
            for dependent in dependency_graph[current]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)
        if len(sorted_plugins) != len(plugins):
            raise RuntimeError("Cycle detected in plugin dependencies.")
        self.execution_order = sorted_plugins
        logger.info("Execution order computed: " + ", ".join(self.execution_order))
        return self.execution_order

    def build_trnx(self):
        """
        Build the active TRNX bot:
          - Create shared memory ports for connected plugin outputs.
          - Wire plugin outputs to inputs.
          - Compute execution order and reorder the plugin list.
          - Call build() on each plugin.
        """
        if self._active_trnx is None:
            raise ValueError("No active TRNX.")
        trnx_name = self._active_trnx._name

        # Setup shared memory ports based on connections.
        for out_plugin, ports in self._plugin_connections[trnx_name].items():
            # Get the output plugin instance.
            output_plugin, _ = self._loaded_plugins[trnx_name][out_plugin]
            for out_port, connections in ports.items():
                # Assume _provided_outputs is defined by the plugin as (shape, dtype)
                shape, dtype = output_plugin._provided_outputs[out_port]
                port_name = f"{out_plugin}_{out_port}"
                port = SharedMemoryPort(port_name, shape, dtype)
                logger.info(f"Created port {port_name} with shape {shape} and dtype {dtype}")
                output_plugin.set_output_port(out_port, port)
                for in_plugin, in_port in connections:
                    input_plugin, _ = self._loaded_plugins[trnx_name][in_plugin]
                    input_plugin.set_input_port(in_port, port)
                    logger.info(f"Connected port {port_name} to {in_plugin}:{in_port}")

        # Compute execution order.
        sorted_plugin_names = self._compute_execution_order()
        ordered_plugins = []
        for pname in sorted_plugin_names:
            plugin_instance, _ = self._loaded_plugins[trnx_name][pname]
            ordered_plugins.append(plugin_instance)
        self._active_trnx.plugins = ordered_plugins

        # Call verify() on each plugin.
        for plugin in self._active_trnx.plugins:
            plugin.verify()
        
        self._active_trnx._is_built = True
        logger.info("TRNX built successfully.")

    def get_trnx(self) -> TRNX:
        """
        Return the active TRNX bot.
        """
        if self._active_trnx is None:
            raise ValueError("No active TRNX.")
        return self._active_trnx

trenex = Trenex()