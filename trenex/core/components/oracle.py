from trenex.core.base.module_base import BaseModule
from core.debug.logger import logger

class Oracle(BaseModule):
    """
    The Oracle is responsible for managing Oracle plugins
    and executing them in the correct order.
    """

    def __init__(self):
        super().__init__("Oracle")

    def attach_plugin(self, plugin: OraclePlugin):
        """
        Attach an Oracle plugin to the Oracle.

        Args:
            plugin (OraclePlugin): The oracle plugin to attach.

        Raises:
            TypeError: If the provided plugin is not an instance of OraclePlugin.
        """
        if not isinstance(plugin, OraclePlugin):
            raise TypeError(f"Invalid plugin type: {type(plugin).__name__}. Expected OraclePlugin.")

        self.plugins.append(plugin)
        logger.info(f"Attached oracle plugin: {plugin.__class__.__name__}")

    def execute(self):
        """
        Execute all attached Oracle plugins in order of priority.
        """
        if not self.plugins:
            logger.warning("No Oracle plugins attached to Oracle.")
            return

        logger.info("Executing Oracle...")

        # Sort plugins by priority before execution
        sorted_plugins = sorted(self.plugins, key=lambda p: p.priority or 0)

        for plugin in sorted_plugins:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
