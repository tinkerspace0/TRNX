# trenex.py
from core.debug.logger import logger
from core.memory import SharedMemoryPort
from core.node.utils import get_available_nodes, create_node_instance
from .trnx import TRNX


class Trenex:
    """
    Node-based Factory for building TRNX trading bots.
    
    - Dynamically manages available nodes (plugins) before execution.
    - Once TRNX is built and running, nodes cannot be modified.
    - Users can modify an existing TRNX object only when it is stopped.
    """
    def __init__(self):
        self._trnx : TRNX = None  # The TRNX instance
        self._saved_trnx = False  # Saved TRNX instance for later use
        self._plugin_connections = {}  # {output_plugin_instance: {output_port: [(input_plugin, input_port)]}}
        self.available_nodes = get_available_nodes()  # Available nodes (plugins)

    def start_new_trnx(self, name: str):
        """Start a new TRNX instance with the given name if none exists."""
        if self._trnx is not None and not self._saved_trnx:
            raise Warning("TRNX instance is not saved. Save it or discard it before starting a new one.")
        self.discard_trnx()  # Discard any existing TRNX instance
        self._trnx = TRNX(name)
        logger.info(f"Started new TRNX: {name}")

    def discard_trnx(self):
        """Discard the current TRNX instance."""
        self._plugin_connections = {}
        self._trnx = None
        self._saved_trnx = False
        logger.info("Discarded TRNX instance.")

    def attach_node(self, node_type: str, node_name: str):
        """Add an available node to the TRNX instance."""
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX while running.")
        
        for _, nodes in self.available_nodes.items():
            if node_name in nodes:
                break
        else:
            raise ValueError(f"Node {node_name} not found in available nodes.")
        
        self._trnx._nodes.append(create_node_instance(node_type, node_name))
        self._trnx._is_built = False  # Has to be rebuilt after any changes
        logger.info(f"Added node {node_name} to TRNX {self._trnx._name}")

    def detach_node(self, node_name: str):
        """Remove a node from the TRNX instance."""
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX while running.")
        
        for node in self._trnx._nodes:
            if node.name == node_name:
                self._trnx._nodes.remove(node)
                logger.info(f"Removed node {node_name} from TRNX {self._trnx._name}")
                self._trnx._is_built = False  # Has to be rebuilt after any changes
                return
        
        raise ValueError(f"Node {node_name} not found in TRNX {self._trnx._name}")

    def connect_node_io(self, output_node, output_port: str, input_node, input_port: str):
        """
        Define an input-output connection between two plugins.
        
        Args:
            output_port: Node instance providing output.
            output_port: Name of the output port.
            input_node: Node instance receiving input.
            input_port: Name of the input port.
        """
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX connections while running.")
        
        if output_node not in self._trnx._nodes:
            raise ValueError(f"The input node {output_node.name} not added to TRNX.")
        if input_node not in self._trnx._nodes:
            raise ValueError(f"The output node {input_node.name} not added to TRNX.")

        # Store the connection
        if output_node not in self._plugin_connections:
            self._plugin_connections[output_node] = {}
        if output_port not in self._plugin_connections[output_node]:
            self._plugin_connections[output_node][output_port] = []
        self._plugin_connections[output_node][output_port].append((input_node, input_port))
        logger.info(f"Defined connection: {output_node.__class__.__name__}:{output_port} -> {input_node.__class__.__name__}:{input_port}")

    def build_trnx(self):
        """
        Finalizes the TRNX configuration:
          - Creates shared memory ports for defined connections.
          - Computes execution order.
          - Calls build() and verify() on each node.
          - Locks further modifications.
        """
        if self._trnx._is_running:
            raise RuntimeError("Cannot build TRNX object while it is running.")

        # Create shared memory ports
        for output_plugin, ports in self._plugin_connections.items():
            for output_port, connections in ports.items():
                key = (output_plugin, output_port)
                if key not in self._shared_memory_ports:
                    shape, dtype = output_plugin._provided_outputs[output_port]
                    port_name = f"{output_plugin.__class__.__name__}_{output_port}"
                    self._shared_memory_ports[key] = SharedMemoryPort(port_name, shape, dtype)
                    logger.info(f"Created shared memory port: {port_name}")

                shared_port = self._shared_memory_ports[key]
                output_plugin.set_output_port(output_port, shared_port)

                for input_plugin, input_port in connections:
                    input_plugin.set_input_port(input_port, shared_port)
                    logger.info(f"Connected {output_plugin.__class__.__name__}:{output_port} -> {input_plugin.__class__.__name__}:{input_port}")

        # Compute execution order
        self._trnx._is_built = True
        self.state = TRNXState.BUILT
        logger.info("TRNX built successfully.")

    def start_execution(self):
        """Starts the execution of TRNX and locks modifications."""
        if self.state != TRNXState.BUILT:
            raise RuntimeError("TRNX must be built before execution.")
        self.state = TRNXState.RUNNING
        self._trnx.run()
        logger.info("TRNX is now running.")

    def stop_execution(self):
        """Stops the execution of TRNX and allows modifications again."""
        if self.state != TRNXState.RUNNING:
            raise RuntimeError("TRNX is not running.")
        self.state = TRNXState.CONFIGURING
        logger.info("TRNX execution stopped. Modifications allowed again.")

    def get_trnx(self) -> TRNX:
        """Return the active TRNX bot."""
        if self._trnx is None:
            raise ValueError("No active TRNX.")
        return self._trnx
