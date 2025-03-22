from core.node.utils.node_discovery import get_available_nodes

if __name__ == "__main__":
    # For testing, print the discovered node implementations.
    nodes = get_available_nodes()
    print("Available node implementations:")
    for category, impls in nodes.items():
        print(f"{category}: {impls}")