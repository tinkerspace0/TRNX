from core.identity import IDGenerator
from core.debug.logger import logger  # 🔥 Import logger

class Namespace:
    """
    A dynamic hierarchical namespace that auto-creates sub-namespaces when accessed.
    Each namespace can contain:
      - Child namespaces (in a dict {name -> Namespace})
      - Child items (in a dict {name -> any Python object})

    'ns_id' is a unique ID from IDGenerator (optional for internal usage).
    """

    def __init__(self, ns_id: str = None):
        self._ns_id = ns_id or IDGenerator.generate_id()
        self._children_ns = {}    # name -> Namespace
        self._children_items = {} # name -> object (int, str, block ID, etc.)

        logger.info(f"Namespace created with ID: {self._ns_id}")

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

    def remove_namespace(self, name: str):
        """
        Remove a child namespace and all of its contents.
        """
        if name not in self._children_ns:
            logger.error(f"Attempted to remove non-existent namespace '{name}'.")
            raise AttributeError(f"No sub-namespace '{name}' exists.")

        del self._children_ns[name]
        logger.info(f"Namespace '{name}' removed.")

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

    def get_item(self, name: str):
        """
        Retrieve the item under 'name'.
        """
        if name not in self._children_items:
            logger.error(f"Attempted to access non-existent item '{name}'.")
            raise AttributeError(f"No item '{name}' found.")

        logger.debug(f"Item '{name}' accessed in namespace.")
        return self._children_items[name]

    def remove_item(self, name: str):
        """
        Delete an item under 'name'.
        """
        if name not in self._children_items:
            logger.error(f"Attempted to remove non-existent item '{name}'.")
            raise AttributeError(f"No item '{name}' to remove.")

        del self._children_items[name]
        logger.info(f"Item '{name}' removed from namespace.")

    def list_contents(self):
        """
        Returns (list_of_subnamespace_names, list_of_item_names).
        """
        namespaces, items = list(self._children_ns.keys()), list(self._children_items.keys())
        logger.debug(f"Namespace listing: {namespaces}, Items: {items}")
        return namespaces, items

    def __getattr__(self, name: str):
        """
        Dot-access for getting:
          - If 'name' is a namespace, return it.
          - If 'name' is an item, return the value.
          - If 'name' does not exist, automatically create a new namespace and return it.
        """
        if name.startswith("_"):
            raise AttributeError(f"Private attribute '{name}' not accessible.")

        if name in self._children_ns:
            return self._children_ns[name]
        if name in self._children_items:
            return self._children_items[name]

        self._children_ns[name] = Namespace()
        logger.info(f"Namespace '{name}' auto-created via dot-access.")
        return self._children_ns[name]

    def __setattr__(self, name: str, value):
        """
        Dot-access for setting:
          - namespace.item_name = some_value  (sets an item)
          - namespace.item_name = None        (removes the item)
        """
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        if value is None:
            self.remove_item(name)
            return

        if name in self._children_ns:
            logger.error(f"Cannot overwrite namespace '{name}' with an item.")
            raise AttributeError(f"Cannot overwrite sub-namespace '{name}' with an item.")

        self._children_items[name] = value
        logger.debug(f"Item '{name}' set via dot-access with value: {value}")

    def __delattr__(self, name: str):
        """
        Allows 'del namespace.name' to remove a sub-namespace or an item.
        """
        if name.startswith("_"):
            super().__delattr__(name)
            return

        if name in self._children_ns:
            del self._children_ns[name]
            logger.info(f"Namespace '{name}' deleted via dot-access.")
            return

        if name in self._children_items:
            del self._children_items[name]
            logger.info(f"Item '{name}' deleted via dot-access.")
            return

        logger.error(f"No attribute '{name}' found to delete.")
        raise AttributeError(f"No attribute '{name}' found to delete.")

class RootNamespace:
    """
    A global root namespace for the application.
    Implements singleton pattern to ensure only one instance exists.
    """

    _instance = None

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

    def create_namespace(self, name: str) -> Namespace:
        """
        Create a new namespace under the root namespace.
        """
        ns = self._root.create_namespace(name)
        logger.info(f"Namespace '{name}' created under RootNamespace.")
        return ns
