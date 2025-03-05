

from trenex.core.base import Plugin

class AgentPlugin(Plugin):
    def __init__(self, config_file = None):
        super().__init__(config_file)