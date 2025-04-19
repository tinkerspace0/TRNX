import networkx as nx
from typing import List, Dict

from core.debug.logger import gl_logger
from core.node.node_io import IOConnection, IO
from core.node.node_base import Node, NodeConfig
from .trnx import TRNX


class TrenexCanvas:
    """
    Node-based Factory for building TRNX trading bots.
    
    - Dynamically manages available nodes (plugins) before execution.
    - Once TRNX is built and running, nodes cannot be modified.
    - Users can modify an existing TRNX object only when it is stopped.
    """
    def __init__(self, name: str, project_dir: str):
        self.name = name
        self._trnx: TRNX = None  # The TRNX instance
        self._node_configs: Dict[str, NodeConfig] = {}  # Dict of node configurations keyed by node name
        self._saved_trnx: bool = False  # Indicates if the TRNX instance has been saved for later use
        self._node_io_connections: List[IOConnection] = []  # List of IOConnection records between nodes
        self._init = False
        self.init_new_trnx(self.name)
    
    def init_new_trnx(self, name: str):
        """Start a new TRNX instance with the given name if none exists."""
        if self._trnx is not None and not self._saved_trnx:
            raise Warning("TRNX instance is not saved. Save it or discard it before starting a new one.")
        if self._init:
            self.discard_trnx()  # Discard any existing TRNX instance
        self._trnx = TRNX(name)
        self._node_configs = {}
        self._node_io_connections = []
        gl_logger.info(f"Started new TRNX: {name}")
 
    def discard_trnx(self):
        """Discard the current TRNX instance."""
        self._node_io_connections = []
        self._trnx = None
        self._node_configs = {}
        self._saved_trnx = False
        gl_logger.info("Discarded TRNX instance.")

    def reset_trnx(self):
        """Reset TRNX by discarding the current instance and starting a new one."""
        self.discard_trnx()
        self.init_new_trnx(self.name)

    def attach_node(self, node: Node):
        """Add an available node to the TRNX instance."""
        if self._trnx is None:
            raise AttributeError("TRNX not initialized")
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX while running.")
        
        self._trnx._nodes.append(node)
        self._trnx._is_built = False  # Requires rebuild after changes
        self._node_configs[node.name] = node.get_config()

        gl_logger.info(f"Added node {node.name} to TRNX {self._trnx.name}")

    def detach_node(self, node_name: str):
        """Remove a node from the TRNX instance."""
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX while running.")
        
        if node_name not in self._node_configs:
            raise ValueError(f"Node {node_name} not found in TRNX {self._trnx.name}")
       
        node = self._node_configs[node_name].node 
        self._trnx._nodes.remove(node)
        self._node_configs.pop(node_name, None)
        
        # Remove any IO connections related to the node. Use the node name extracted from each IO’s parent NodeIO.
        self._node_io_connections = [
            conn for conn in self._node_io_connections 
            if conn.out_IO.parent._node.name != node_name and conn.in_IO.parent._node.name != node_name
        ]

        gl_logger.info(f"Removed node {node_name} from TRNX {self._trnx.name}")
        self._trnx._is_built = False  # Requires rebuild after changes

    def connect_node_io(self, out_io: IO, in_io: IO):
        """
        Connect an output IO to an input IO.
        
        This method validates that the provided IOs belong to nodes registered in the TRNX instance,
        ensures they are of the correct types (OUTPUT for out_io and INPUT for in_io), invokes the IO's 
        own connect method for mutual connection, and then creates an IOConnection record.
        """
        if self._trnx._is_running:
            raise RuntimeError("Cannot modify TRNX connections while running.")

        # Retrieve node names from each IO's parent NodeIO.
        out_node_name = out_io.parent._node.name
        in_node_name = in_io.parent._node.name

        if out_node_name not in self._node_configs:
            raise ValueError(f"Output node {out_node_name} not found in TRNX.")
        if in_node_name not in self._node_configs:
            raise ValueError(f"Input node {in_node_name} not found in TRNX.")

        # Validate port types.
        if out_io._io_type != IO.IOType.OUTPUT:
            raise ValueError(f"The provided port '{out_io.name}' is not an OUTPUT port.")
        if in_io._io_type != IO.IOType.INPUT:
            raise ValueError(f"The provided port '{in_io.name}' is not an INPUT port.")

        # Establish the connection using the IO's connect method.
        out_io.connect(in_io)

        # Create and record the connection.
        connection = IOConnection(out_IO=out_io, in_IO=in_io)
        self._node_io_connections.append(connection)
        gl_logger.info(f"Defined connection: {out_node_name}:{out_io.name} -> {in_node_name}:{in_io.name}")

    def build_trnx(self):
        """
        Finalizes the TRNX configuration:
          - (Optional) Creates shared memory ports for defined connections.
          - Builds a Directed Acyclic Graph (DAG) representing execution order based on node connections.
          - Locks further modifications.
        """
        if self._trnx._is_running:
            raise RuntimeError("Cannot build TRNX object while it is running.")

        # (Optional) Create shared memory ports for connections here.
        # TODO: Implement shared memory port creation logic if needed.

        # Verify that all nodes are correctly set up.
        for node in self._trnx._nodes:
            node.verify()

        # Build the DAG for execution ordering.
        dag = nx.DiGraph()

        # Add all nodes to the graph.
        for node in self._trnx._nodes:
            dag.add_node(node)

        # Add edges according to the defined IO connections.
        for connection in self._node_io_connections:
            out_node = connection.out_IO.parent._node
            in_node = connection.in_IO.parent._node
            dag.add_edge(out_node, in_node)

        # Validate that the resulting graph is acyclic.
        if not nx.is_directed_acyclic_graph(dag):
            raise ValueError("The node dependency graph has cycles! Ensure dependencies are acyclic.")

        # Assign the execution graph to the TRNX instance.
        self._trnx._exec_graph = dag

        self._trnx._is_built = True
        gl_logger.info("TRNX built successfully with DAG execution order.")

    def get_trnx(self) -> TRNX:
        """Return the active TRNX bot."""
        if self._trnx is None:
            raise ValueError("No active TRNX.")
        return self._trnx