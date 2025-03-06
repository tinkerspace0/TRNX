# trnx.py
from core.debug.logger import logger

class TRNX:
    """
    TRNX is the final trading bot object that simply runs its plugins.
    Once built, all the plugins are arranged in the correct order,
    and run() will simply execute each plugin's process() method.
    """
    def __init__(self, name: str):
        self.name = name
        self.plugins = []  # List of plugin instances in execution order

    def run(self):
        logger.info(f"Running TRNX bot: {self.name}")
        for plugin in self.plugins:
            logger.info(f"Executing plugin: {plugin.__class__.__name__}")
            plugin.process()
