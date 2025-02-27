from core.identity import IDGenerator

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

    def create_namespace(self, name: str) -> "Namespace":
        """
        Explicitly create a sub-namespace under 'name' (if not already created).
        """
        if name in self._children_items:
            raise AttributeError(
                f"Cannot create namespace '{name}' because an item with that name already exists."
            )
        if name not in self._children_ns:
            self._children_ns[name] = Namespace()
        return self._children_ns[name]

    def remove_namespace(self, name: str):
        """
        Remove a child namespace and all of its contents.
        """
        if name not in self._children_ns:
            raise AttributeError(f"No sub-namespace '{name}' exists.")
        del self._children_ns[name]

    def set_item(self, name: str, value):
        """
        Store 'value' (any Python object) under 'name'.
        Raises error if a sub-namespace with that name already exists.
        """
        if name in self._children_ns:
            raise AttributeError(
                f"Cannot set item '{name}' because a sub-namespace with that name exists."
            )
        self._children_items[name] = value

    def get_item(self, name: str):
        """
        Retrieve the item under 'name'.
        """
        if name not in self._children_items:
            raise AttributeError(f"No item '{name}' found.")
        return self._children_items[name]

    def remove_item(self, name: str):
        """
        Delete an item under 'name'.
        """
        if name not in self._children_items:
            raise AttributeError(f"No item '{name}' to remove.")
        del self._children_items[name]

    def list_contents(self):
        """
        Returns (list_of_subnamespace_names, list_of_item_names).
        """
        return list(self._children_ns.keys()), list(self._children_items.keys())

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
            raise AttributeError(
                f"Cannot overwrite sub-namespace '{name}' with an item."
            )
        self._children_items[name] = value

    def __delattr__(self, name: str):
        """
        Allows 'del namespace.name' to remove a sub-namespace or an item.
        """
        if name.startswith("_"):
            super().__delattr__(name)
            return
        if name in self._children_ns:
            del self._children_ns[name]
            return
        if name in self._children_items:
            del self._children_items[name]
            return
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
        return self._root.create_namespace(name)
