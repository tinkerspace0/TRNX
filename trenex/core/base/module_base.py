from abc import ABC


class BaseModule(ABC):
    """
    Base class for all components.
    Each component maintains a list of plugins.
    """
    def __init__(self, name):
        self.name = name
        self.plugins = []  # List of plugins
        self.plugin_order = []  # Order in which plugins should be executed

    def attach_plugin(self, plugin):
        """
        Attach a plugin to the component.
        Plugin must declare its dependencies and output its execution order.
        """
        if plugin not in self.plugins:
            self.plugins.append(plugin)

    def _update_plugin_order(self):
        """
        Determine the order in which plugins should run based on dependencies.
        For example, data processing plugins must run before strategy plugins.
        This can be as simple or as sophisticated as needed.
        """
        # A simple strategy: sort by a plugin attribute (e.g., priority)
        self.plugin_order = sorted(self.plugins, key=lambda p: p.priority)

    def build(self):
        """
        Finalize component setup.
        Plugins can perform final configuration here.
        """
        for plugin in self.plugins:
            plugin.build()
        self._update_plugin_order()
        

    def execute(self):
        """
        Execute the plugins in the defined order.
        """
        print(f"Executing {self.name} Component:")
        for plugin in self.plugin_order:
            plugin.process()
