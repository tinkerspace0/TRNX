from trenex.core.base.module_base import BaseModule
from trenex.core.plugin.exchange_plugin import ExchangeInterface
from trenex.core.debug.logger import logger

class ExchangeComponent(BaseModule):
    """
    The ExchangeComponent is responsible for managing ExchangeInterface plugins
    and executing them in the correct order.
    """

    def __init__(self):
        super().__init__("ExchangeComponent")

    def attach_plugin(self, plugin: ExchangeInterface):
        """
        Attach an ExchangeInterface plugin to the ExchangeComponent.

        Args:
            plugin (ExchangeInterface): The exchange plugin to attach.

        Raises:
            TypeError: If the provided plugin is not an instance of ExchangeInterface.
        """
        if not isinstance(plugin, ExchangeInterface):
            raise TypeError(f"Invalid plugin type: {type(plugin).__name__}. Expected ExchangeInterface.")

        self.plugins.append(plugin)
        logger.info(f"Attached exchange plugin: {plugin.__class__.__name__}")

    def execute(self):
        """
        Execute all attached ExchangeInterface plugins in order of priority.
        """
        if not self.plugins:
            logger.warning("No exchange plugins attached to ExchangeComponent.")
            return

        logger.info("Executing ExchangeComponent...")

        # Sort plugins by priority before execution
        sorted_plugins = sorted(self.plugins, key=lambda p: p.priority or 0)

        for plugin in sorted_plugins:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
