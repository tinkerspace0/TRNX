from typing import List
from core.node.node_base import Node
from core.debug.logger import gl_logger as logger
import networkx as nx
import threading

class TRNX:
    """
    TRNX is the final trading bot object that holds nodes and executes them using a DAG.
    Once built, the configuration (nodes and their connections) is locked.
    """
    def __init__(self, name: str):
        self.name = name
        self._nodes: List[Node] = []       # List of node instances.
        self._exec_graph = None                 # DAG representing node dependencies.
        self._is_built = False
        self._is_running = False
        self._stop = False                 # Flag for stopping continuous run.

    def run_once(self):
        logger.info(f"Running TRNX bot: {self.name} for one iteration")
        if not self._is_built:
            raise ValueError("TRNX is not built. Please build the TRNX first.")
        if self._is_running:
            raise RuntimeError("TRNX is already running. Stop it before running again.")
        if self._exec_graph is None:
            raise ValueError("DAG not configured. TRNXFactory must build the DAG.")

        self._is_running = True
        # Create a copy of the DAG for execution
        graph_copy = self._exec_graph.copy()

        # Execute nodes level-by-level (all nodes with no incoming edges run concurrently)
        while graph_copy.nodes:
            ready_nodes = [node for node in graph_copy.nodes if graph_copy.in_degree(node) == 0]
            threads = []
            for node in ready_nodes:
                logger.info(f"Executing node: {node.__class__.__name__}")
                t = threading.Thread(target=node.process)
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            # Remove executed nodes to reveal next level
            graph_copy.remove_nodes_from(ready_nodes)
        self._is_running = False

    def run(self):
        logger.info(f"Running TRNX bot: {self.name}")
        if not self._is_built:
            raise ValueError("TRNX is not built. Please build the TRNX first.")
        if self._is_running:
            raise RuntimeError("TRNX is already running. Stop it before running again.")
        if self._exec_graph is None:
            raise ValueError("DAG not configured. TRNXFactory must build the DAG.")

        self._is_running = True
        # Continuous run: repeatedly execute one iteration of the DAG.
        while not self._stop:
            graph_copy = self._exec_graph.copy()
            while graph_copy.nodes:
                ready_nodes = [node for node in graph_copy.nodes if graph_copy.in_degree(node) == 0]
                threads = []
                for node in ready_nodes:
                    logger.info(f"Executing node: {node.__class__.__name__}")
                    t = threading.Thread(target=node.process)
                    t.start()
                    threads.append(t)
                for t in threads:
                    t.join()
                graph_copy.remove_nodes_from(ready_nodes)
        self._is_running = False
