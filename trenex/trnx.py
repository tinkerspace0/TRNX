# trnx.py
from core.debug.logger import logger

class TRNX:
    """
    TRNX is the final trading bot object that simply runs its plugins.
    Once built, all the plugins are arranged in the correct order,
    and run() will simply execute each plugin's process() method.
    """
    def __init__(self, name: str):
        self._name = name
        self._plugins = []  # List of plugin instances in execution order
        self._is_built = False

    def run(self):
        logger.info(f"Running TRNX bot: {self._name}")
        for plugin in self._plugins:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
