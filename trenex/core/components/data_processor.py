from trenex.core.base.module_base import BaseModule
from trenex.modules.data_processor.data_processor_plugin import DataProcessorPlugin
from core.debug.logger import logger


class DataProcessor(BaseModule):
    """
    The DataProcessorComponent is responsible for managing and executing 
    DataProcessorPlugins in the correct order.
    """

    def __init__(self):
        super().__init__("DataProcessorComponent")

    def attach_plugin(self, plugin: DataProcessorPlugin):
        """
        Attach a DataProcessorPlugin to the DataProcessorComponent.

        Args:
            plugin (DataProcessorPlugin): The data processing plugin to attach.

        Raises:
            TypeError: If the provided plugin is not an instance of DataProcessorPlugin.
        """
        if not isinstance(plugin, DataProcessorPlugin):
            raise TypeError(f"Invalid plugin type: {type(plugin).__name__}. Expected DataProcessorPlugin.")

        self.plugins.append(plugin)
        logger.info(f"Attached data processor plugin: {plugin.__class__.__name__}")

    def execute(self):
        """
        Execute all attached DataProcessorPlugins in order of priority.
        """
        if not self.plugins:
            logger.warning("No data processor plugins attached to DataProcessorComponent.")
            return

        logger.info("Executing DataProcessorComponent...")

        # Sort plugins by priority before execution
        sorted_plugins = sorted(self.plugins, key=lambda p: p.priority or 0)

        for plugin in sorted_plugins:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
