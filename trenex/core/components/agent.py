from trenex.core.base.module_base import BaseModule
from core.debug.logger import logger

class Agent(BaseModule):
    """
    The Agent is responsible for managing Agent plugins
    and executing them in the correct order.
    """

    def __init__(self):
        super().__init__("Agent")

    def attach_plugin(self, plugin):
        """
        Attach an Agent plugin to the Agent.

        Args:
            plugin (Agent Plugin): The agent plugin to attach.

        Raises:
            TypeError: If the provided plugin is not an instance of Agent Plugin.
        """
        if not isinstance(plugin, AgentPlugin):
            raise TypeError(f"Invalid plugin type: {type(plugin).__name__}. Expected AgentPlugin.")

        self.plugins.append(plugin)
        logger.info(f"Attached agent plugin: {plugin.__class__.__name__}")

    def execute(self):
        """
        Execute all attached Agent plugins in order of priority.
        """
        if not self.plugins:
            logger.warning("No exchange plugins attached to Agent.")
            return

        logger.info("Executing Agent...")

        # Sort plugins by priority before execution
        sorted_plugins = sorted(self.plugins, key=lambda p: p.priority or 0)

        for plugin in sorted_plugins:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
