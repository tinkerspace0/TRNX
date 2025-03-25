import networkx as nx
from typing import List, Dict

from core.debug.logger import gl_logger
from core.node.utils import get_available_nodes, create_node_instance
from core.node.node_io import IOConnection
from core.node.node_base import Node, NodeConfig
from .trnx import TRNX


class TRNXEditor:
    """
    Node-based Factory for building TRNX trading bots.
    
    - Dynamically manages available nodes (plugins) before execution.
    - Once TRNX is built and running, nodes cannot be modified.
    - Users can modify an existing TRNX object only when it is stopped.
    """
    def __init__(self):
        self._trnx: TRNX = None  # The TRNX instance
        self._node_configs: Dict[str, NodeConfig] = {}  # Dict of node configurations
        self._saved_trnx: bool = False  # Saved TRNX instance for later use
        self._node_io_connections: List[IOConnection] = []  # List of IO connections between nodes

    def start_new_trnx(self, name: str):
        """Start a new TRNX instance with the given name if none exists."""
        if self._trnx is not None and not self._saved_trnx:
            raise Warning("TRNX instance is not saved. Save it or discard it before starting a new one.")
        self.discard_trnx()  # Discard any existing TRNX instance
        self._trnx = TRNX(name)
        self._node_configs = {}
        gl_logger.info(f"Started new TRNX: {name}")

    def discard_trnx(self):
        """Discard the current TRNX instance."""
        self._node_io_connections = []
        self._trnx = None
        self._node_configs = {}
        self._saved_trnx = False
        gl_logger.info("Discarded TRNX instance.")

    def attach_node(self, node_type: str, node_name: str):
        """Add an available node to the TRNX instance."""
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX while running.")
        
        for _, nodes in get_available_nodes().items():
            if node_name in nodes:
                break
        else:
            raise ValueError(f"Node {node_name} not found in available nodes.")
        
        node_instance = create_node_instance(node_type, node_name)
        self._trnx._nodes.append(node_instance)
        self._trnx._is_built = False  # Requires rebuild after changes
        self._node_configs[node_instance.name] = node_instance.get_config()

        gl_logger.info(f"Added node {node_name} to TRNX {self._trnx.name}")

    def detach_node(self, node_name: str):
        """Remove a node from the TRNX instance."""
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX while running.")
        
        if node_name not in self._node_configs:
            raise ValueError(f"Node {node_name} not found in TRNX {self._trnx.name}")
       
        node = self._node_configs[node_name].node 
        self._trnx._nodes.remove(node)
        self._node_configs.pop(node_name, None)
        
        # Remove any IO connections related to this node.
        self._node_io_connections = [
            conn for conn in self._node_io_connections 
            if conn.output_node.name != node_name and conn.input_node.name != node_name
        ]

        gl_logger.info(f"Removed node {node_name} from TRNX {self._trnx.name}")
        self._trnx._is_built = False  # Requires rebuild after changes

    def connect_node_io(self, output_node_name: str, output_port: str, input_node_name: str, input_port: str):
        """
        Define an input-output connection between two nodes using their names.
        
        This method looks up the node instances, validates that the ports exist,
        creates an IOConnection record, and stores it.
        """
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX connections while running.")

        if output_node_name not in self._node_configs:
            raise ValueError(f"Output node {output_node_name} not found in TRNX.")
        if input_node_name not in self._node_configs:
            raise ValueError(f"Input node {input_node_name} not found in TRNX.")

        # Get the NodeIO interfaces from the node configuration.
        output_ios = self._node_configs[output_node_name].output_ios
        input_ios = self._node_configs[input_node_name].input_ios

        # Validate that the specified ports exist.
        try:
            output_ios.get(output_port)
        except KeyError:
            raise ValueError(f"Output port '{output_port}' not found in node '{output_node_name}'.")
        try:
            input_ios.get(input_port)
        except KeyError:
            raise ValueError(f"Input port '{input_port}' not found in node '{input_node_name}'.")

        # Resolve the actual node instances from the node configuration.
        output_node = self._node_configs[output_node_name].node
        input_node = self._node_configs[input_node_name].node

        # Create the connection record.
        connection = IOConnection(
            output_node=output_node,
            output_port=output_port,
            input_node=input_node,
            input_port=input_port
        )
        self._node_io_connections.append(connection)
        gl_logger.info(f"Defined connection: {output_node_name}:{output_port} -> {input_node_name}:{input_port}")

    def build_trnx(self):
        """
        Finalizes the TRNX configuration:
          - Creates shared memory ports for defined connections (if applicable).
          - Builds the DAG representing execution order based on node connections.
          - Locks further modifications.
        """
        if self._trnx._is_running:
            raise RuntimeError("Cannot build TRNX object while it is running.")

        # (Optional) Create shared memory ports for connections here.
        # TODO: Implement shared memory port creation logic if needed.

        # Verify that all nodes are set up correctly.
        for node in self._trnx._nodes:
            node.verify()

        # Build the DAG for execution order.
        dag = nx.DiGraph()

        # Add all nodes to the graph.
        for node in self._trnx._nodes:
            dag.add_node(node)

        # Add edges based on defined node connections.
        for connection in self._node_io_connections:
            dag.add_edge(connection.output_node, connection.input_node)

        # Validate that the DAG is acyclic.
        if not nx.is_directed_acyclic_graph(dag):
            raise ValueError("The node dependency graph has cycles! Ensure dependencies are acyclic.")

        # Assign the DAG to the TRNX instance.
        self._trnx._exec_graph = dag

        self._trnx._is_built = True
        gl_logger.info("TRNX built successfully with DAG execution order.")

    def get_trnx(self) -> TRNX:
        """Return the active TRNX bot."""
        if self._trnx is None:
            raise ValueError("No active TRNX.")
        return self._trnx