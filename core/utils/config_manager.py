import json
import os
from core.debug.logger import logger
from core.debug.profiler import Profiler

class ConfigManager:
    """Handles loading, saving, and updating configuration files."""
    
    CONFIG_FILE = "config.json"

    def __init__(self):
        logger.info("Initializing ConfigManager...")
        self.config = self._load_config()

    @Profiler.profile  # ⏱️ Profile execution time
    def _load_config(self):
        """Load configuration from a JSON file."""
        if not os.path.exists(self.CONFIG_FILE):
            logger.warning(f"Configuration file '{self.CONFIG_FILE}' not found. Using default config.")
            return {}  # Return empty config if file doesn't exist
        try:
            with open(self.CONFIG_FILE, "r") as f:
                data = json.load(f)
                logger.info(f"Configuration loaded successfully from '{self.CONFIG_FILE}'.")
                return data
        except Exception as e:
            logger.error(f"Failed to load config file: {e}")
            return {}

    @Profiler.profile  # ⏱️ Profile execution time
    def save_config(self):
        """Save the current configuration to the file."""
        try:
            with open(self.CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
            logger.info(f"Configuration saved successfully to '{self.CONFIG_FILE}'.")
        except Exception as e:
            logger.error(f"Failed to save config file: {e}")

    @Profiler.profile  # ⏱️ Profile execution time
    def get(self, key, default=None):
        """Retrieve a configuration value using dot notation."""
        keys = key.split(".")
        data = self.config
        for k in keys:
            if k in data:
                data = data[k]
            else:
                logger.warning(f"Config key '{key}' not found. Returning default: {default}")
                return default
        logger.debug(f"Retrieved config value for '{key}': {data}")
        return data

    @Profiler.profile  # ⏱️ Profile execution time
    def set(self, key, value):
        """Update a configuration value using dot notation."""
        keys = key.split(".")
        data = self.config
        for k in keys[:-1]:
            data = data.setdefault(k, {})
        data[keys[-1]] = value
        self.save_config()
        logger.info(f"Updated config key '{key}' with value: {value}")

# Global instance
config = ConfigManager()
