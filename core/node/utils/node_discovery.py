# core/node/utils/node_discovery.py
import os
import importlib
import inspect
from typing import Dict, List

from core.node.node_base import Node

def get_available_nodes() -> Dict[str, List[str]]:
    """
    Scan the core/node/nodes folder and return a dictionary mapping each node category
    (subfolder name) to a list of available node implementation class names.
    
    Example return value:
        {
            "exchanges": ["Binance", "Coinbase"],
            "dataprocessors": ["RSINode", "VolumeProcessor"],
            "agents": ["AgentNode"],
            "oracles": ["OracleNode", "MLOracle"]
        }
    """
    # Determine the base directory for node implementations.
    base_dir = os.path.join(os.path.dirname(__file__), "..", "nodes")
    available_nodes = {}

    if not os.path.exists(base_dir):
        raise FileNotFoundError(f"Nodes directory not found: {base_dir}")

    # Iterate over each subfolder (each representing a node category)
    for category in os.listdir(base_dir):
        category_dir = os.path.join(base_dir, category)
        if os.path.isdir(category_dir):
            available_nodes[category] = []
            # List all .py files in the category directory, excluding __init__.py.
            for fname in os.listdir(category_dir):
                if fname.endswith(".py") and fname != "__init__.py":
                    module_name = os.path.splitext(fname)[0]
                    # Build the full module path, e.g., core.node.nodes.exchange.Binance
                    full_module_path = f"core.node.nodes.{category}.{module_name}"
                    try:
                        module = importlib.import_module(full_module_path)
                    except ImportError as e:
                        print(f"Error importing module {full_module_path}: {e}")
                        continue
                    # Inspect the module for classes that are subclasses of Node (but not Node itself).
                    for name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                        if cls.__module__ == full_module_path and issubclass(cls, Node) and cls is not Node:
                            available_nodes[category].append(name)
    return available_nodes

