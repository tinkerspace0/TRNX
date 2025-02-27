from core.identity import IDGenerator
from core.debug.logger import logger
from core.debug.profiler import Profiler

class Namespace:
    """
    A dynamic hierarchical namespace that auto-creates sub-namespaces when accessed.
    Each namespace can contain:
      - Child namespaces (in a dict {name -> Namespace})
      - Child items (in a dict {name -> any Python object})

    'ns_id' is a unique ID from IDGenerator (optional for internal usage).
    """

    @Profiler.profile   
    def __init__(self, ns_id: str = None):
        self._ns_id = ns_id or IDGenerator.generate_id()
        self._children_ns = {}    # name -> Namespace
        self._children_items = {} # name -> object (int, str, block ID, etc.)

        logger.info(f"Namespace created with ID: {self._ns_id}")

    @Profiler.profile   
    def create_namespace(self, name: str) -> "Namespace":
        """
        Explicitly create a sub-namespace under 'name' (if not already created).
        """
        if name in self._children_items:
            logger.warning(f"Cannot create namespace '{name}', item with the same name exists.")
            raise AttributeError(f"Cannot create namespace '{name}' because an item with that name already exists.")

        if name not in self._children_ns:
            self._children_ns[name] = Namespace()
            logger.info(f"Namespace '{name}' created.")

        return self._children_ns[name]

    @Profiler.profile   
    def remove_namespace(self, name: str):
        """
        Remove a child namespace and all of its contents.
        """
        if name not in self._children_ns:
            logger.error(f"Attempted to remove non-existent namespace '{name}'.")
            raise AttributeError(f"No sub-namespace '{name}' exists.")

        del self._children_ns[name]
        logger.info(f"Namespace '{name}' removed.")

    @Profiler.profile   
    def set_item(self, name: str, value):
        """
        Store 'value' (any Python object) under 'name'.
        Raises error if a sub-namespace with that name already exists.
        """
        if name in self._children_ns:
            logger.error(f"Cannot set item '{name}', a namespace with the same name exists.")
            raise AttributeError(f"Cannot set item '{name}' because a sub-namespace with that name exists.")

        self._children_items[name] = value
        logger.debug(f"Item '{name}' set in namespace with value: {value}")

    @Profiler.profile   
    def get_item(self, name: str):
        """
        Retrieve the item under 'name'.
        """
        if name not in self._children_items:
            logger.error(f"Attempted to access non-existent item '{name}'.")
            raise AttributeError(f"No item '{name}' found.")

        logger.debug(f"Item '{name}' accessed in namespace.")
        return self._children_items[name]

    @Profiler.profile   
    def remove_item(self, name: str):
        """
        Delete an item under 'name'.
        """
        if name not in self._children_items:
            logger.error(f"Attempted to remove non-existent item '{name}'.")
            raise AttributeError(f"No item '{name}' to remove.")

        del self._children_items[name]
        logger.info(f"Item '{name}' removed from namespace.")

    @Profiler.profile   
    def list_contents(self):
        """
        Returns (list_of_subnamespace_names, list_of_item_names).
        """
        namespaces, items = list(self._children_ns.keys()), list(self._children_items.keys())
        logger.debug(f"Namespace listing: {namespaces}, Items: {items}")
        return namespaces, items

class RootNamespace:
    """
    A global root namespace for the application.
    Implements singleton pattern to ensure only one instance exists.
    """

    _instance = None

    @Profiler.profile   
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RootNamespace, cls).__new__(cls)
            cls._instance._root = Namespace()
            logger.info("RootNamespace initialized.")
        return cls._instance

    def __getattr__(self, name: str):
        """
        Delegate attribute access to the root namespace.
        """
        return getattr(self._root, name)

    def __setattr__(self, name: str, value):
        """
        Delegate attribute setting to the root namespace.
        """
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            setattr(self._root, name, value)

    @Profiler.profile   
    def create_namespace(self, name: str) -> Namespace:
        """
        Create a new namespace under the root namespace.
        """
        ns = self._root.create_namespace(name)
        logger.info(f"Namespace '{name}' created under RootNamespace.")
        return ns
