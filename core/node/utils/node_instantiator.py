# core/node/utils/node_instantiator.py
import importlib

from core.utils import camel_to_snake

def create_node_instance(category: str, node_class_name: str, **kwargs):
    """
    Create an instance of a Node given the node category and node class name.
    
    Args:
        category (str): The node category (e.g., "exchange", "dataprocessor", "agent", "oracle").
        node_class_name (str): The name of the node class (e.g., "Binance", "RSINode", "AgentNode").
        **kwargs: Additional keyword arguments to pass to the node constructor.
    
    Returns:
        An instance of the node.
    
    Raises:
        ImportError: If the module or class cannot be imported.
        AttributeError: If the node class is not found in the module.
    """
    # Convert node_class_name to snake_case to form the module filename.
    module_filename = camel_to_snake(node_class_name)
    # Build the full module path. For example: "core.node.nodes.exchange.binance"
    full_module_path = f"core.node.nodes.{category}.{module_filename}"
    try:
        module = importlib.import_module(full_module_path)
    except ImportError as e:
        raise ImportError(f"Could not import module '{full_module_path}'. Ensure the file exists.") from e
    
    try:
        node_class = getattr(module, node_class_name)
    except AttributeError as e:
        raise AttributeError(f"Module '{full_module_path}' does not have a class named '{node_class_name}'.") from e
    
    return node_class(**kwargs)

# Example usage:
if __name__ == "__main__":
    # Suppose you have an exchange node named "Binance" under the "exchange" category.
    try:
        instance = create_node_instance("exchange", "Binance")
        print(f"Created node instance: {instance}")
    except Exception as e:
        print(f"Error creating node instance: {e}")