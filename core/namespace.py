from core.identity import IDGenerator
from core.debug.logger import logger
from core.debug.profiler import Profiler
from core.shared_memory import SharedMemoryPort

class Namespace:
    """
    A hierarchical namespace system that only allows sub-namespaces or SharedMemoryPort objects.
    Supports dynamic creation of namespaces when accessed via dot notation.
    """

    @Profiler.profile
    def __init__(self, name: str, parent=None):
        """
        Initialize a Namespace.

        Args:
            name (str): Name of the namespace.
            parent (Namespace, optional): Parent namespace. If None, assigns RootNamespace.
        """
        self._name = name
        self._ns_id = IDGenerator.generate_id()
        self._children_ns = {}  # name -> Namespace
        self._children_ports = {}  # name -> SharedMemoryPort

        # Ensure all namespaces belong to RootNamespace
        self._parent = parent if parent else RootNamespace()._root

        logger.info(f"Namespace '{self._name}' created (Parent: {self._parent._name}).")

    @Profiler.profile
    def create_namespace(self, name: str) -> "Namespace":
        """Create or return a sub-namespace."""
        if name in self._children_ports:
            raise AttributeError(f"Cannot create namespace '{name}', a SharedMemoryPort with that name exists.")

        if name not in self._children_ns:
            self._children_ns[name] = Namespace(name, parent=self)
            logger.info(f"Namespace '{name}' created under '{self._name}'.")

        return self._children_ns[name]

    @Profiler.profile
    def attach_shared_memory(self, name: str, shape: tuple, dtype=float):
        """Attach a SharedMemoryPort to this namespace."""
        if name in self._children_ns:
            raise AttributeError(f"Cannot attach SharedMemoryPort '{name}', a namespace with that name exists.")

        if name not in self._children_ports:
            self._children_ports[name] = SharedMemoryPort(name, shape, dtype)
            logger.info(f"SharedMemoryPort '{name}' attached to namespace '{self._name}'.")

    @Profiler.profile
    def remove_namespace(self, name: str):
        """Remove a namespace and all its children, including SharedMemoryPorts."""
        if name not in self._children_ns:
            raise AttributeError(f"No sub-namespace '{name}' exists.")

        self._children_ns[name]._recursive_cleanup()
        del self._children_ns[name]
        logger.info(f"Namespace '{name}' removed from '{self._name}'.")

    @Profiler.profile
    def _recursive_cleanup(self):
        """Recursively remove all child namespaces and SharedMemoryPorts."""
        for ns_name in list(self._children_ns.keys()):
            self._children_ns[ns_name]._recursive_cleanup()
            del self._children_ns[ns_name]

        for port_name in list(self._children_ports.keys()):
            self._children_ports[port_name].close()
            self._children_ports[port_name].unlink()
            del self._children_ports[port_name]
            logger.info(f"SharedMemoryPort '{port_name}' unlinked and removed.")

    @Profiler.profile
    def __getattr__(self, name: str):
        """
        Allows dynamic access to namespaces.
        Example: RootNamespace().Exchange.Binance will auto-create Exchange and Binance if they do not exist.
        """
        if name in self._children_ports:
            return self._children_ports[name]

        if name not in self._children_ns:
            self._children_ns[name] = Namespace(name, parent=self)
            logger.info(f"Auto-created namespace '{name}' under '{self._name}'.")

        return self._children_ns[name]

    @Profiler.profile
    def __setattr__(self, name: str, value):
        """
        Allows dynamic assignment of SharedMemoryPort.
        Example: RootNamespace().Exchange.Binance.Ticker = SharedMemoryPort()
        """
        if name.startswith("_"):
            super().__setattr__(name, value)
        elif isinstance(value, SharedMemoryPort):
            if name in self._children_ns:
                raise AttributeError(f"Cannot assign SharedMemoryPort '{name}', a namespace with that name exists.")
            self._children_ports[name] = value
            logger.info(f"Assigned SharedMemoryPort '{name}' in namespace '{self._name}'.")
        else:
            raise ValueError("Only SharedMemoryPort instances can be assigned.")

    @Profiler.profile
    def __delattr__(self, name: str):
        """
        Allows `del namespace.item` to remove namespaces or SharedMemoryPorts.
        """
        if name in self._children_ns:
            self.remove_namespace(name)
        elif name in self._children_ports:
            self._children_ports[name].close()
            self._children_ports[name].unlink()
            del self._children_ports[name]
            logger.info(f"Deleted SharedMemoryPort '{name}' from namespace '{self._name}'.")
        else:
            raise AttributeError(f"No attribute '{name}' found to delete.")

class RootNamespace:
    """
    Singleton RootNamespace ensuring all namespaces are under it.
    """

    _instance = None

    @Profiler.profile
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RootNamespace, cls).__new__(cls)
            cls._instance._root = Namespace("Root", parent=None)
            logger.info("RootNamespace initialized.")
        return cls._instance

    def __getattr__(self, name: str):
        """Delegate attribute access to the root namespace."""
        return getattr(self._root, name)

    def __setattr__(self, name: str, value):
        """Delegate attribute setting to the root namespace."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            setattr(self._root, name, value)

    @Profiler.profile
    def create_namespace(self, name: str) -> Namespace:
        """Create a new namespace under the root."""
        ns = self._root.create_namespace(name)
        logger.info(f"Namespace '{name}' created under RootNamespace.")
        return ns
