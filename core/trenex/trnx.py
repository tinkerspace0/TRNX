# trenex/trnx.py

from enum import Enum
from typing import List
from core.node.node_base import Node
from core.debug.logger import gl_logger as logger

class TRNX:
    """
    TRNX is the final trading bot object that holds nodes and executes them.
    Once built, the configuration (nodes and their connections) is locked.
    """
    def __init__(self, name: str):
        self.name = name
        # TODO: Change _nodes format to facilitate parallel execution
        # TODO: Implement parallel execution of nodes when possible
        self._nodes: List[Node] = []  # This will hold Node instances.
        self._is_built = False
        self._is_running = False

    def run_once(self):
        logger.info(f"Running TRNX bot: {self.name} for one iteration")
        if not self._is_built:
            raise ValueError("TRNX is not built. Please build the TRNX first.")
        if self._is_running:
            raise RuntimeError("TRNX is already running. Stop it before running again.")
        self._is_running = True
        for node in self._nodes:
            logger.info(f"Executing node: {node.__class__.__name__}")
            node.process()
        self._is_running = False

    def run(self):
        logger.info(f"Running TRNX bot: {self.name}")
        if not self._is_built:
            raise ValueError("TRNX is not built. Please build the TRNX first.")
        if self._is_running:
            raise RuntimeError("TRNX is already running. Stop it before running again.")
        self._is_running = True
        while self._is_running:
            for node in self._nodes:
                logger.info(f"Executing node: {node.__class__.__name__}")
                node.process()
            self._is_running = False