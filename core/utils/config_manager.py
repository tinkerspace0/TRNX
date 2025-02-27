import json
import os
import threading
from core.debug.logger import logger

class ConfigManager:
    """Manages both general and component-specific configuration files with per-file locks."""

    ROOT_CONFIG_PATH = "configs/"  # General bot configs
    MODULE_CONFIG_PATH = "modules/"  # Component-specific configs

    _loaded_configs = {}  # Cache for in-memory config modifications
    _locks = {}  # Dictionary of locks per config file

    @staticmethod
    def _get_config_path(config_name: str, module: str = None):
        """Determine the correct file path for a config."""
        if module:
            return os.path.join(ConfigManager.MODULE_CONFIG_PATH, module, f"{config_name}.json")
        return os.path.join(ConfigManager.ROOT_CONFIG_PATH, f"{config_name}.json")

    @staticmethod
    def _get_lock(config_file: str):
        """Retrieve or create a lock for a specific config file."""
        if config_file not in ConfigManager._locks:
            ConfigManager._locks[config_file] = threading.Lock()
        return ConfigManager._locks[config_file]

    @staticmethod
    def load_config(config_name: str, module: str = None):
        """
        Load a JSON config file dynamically in a thread-safe way.

        Args:
            config_name (str): The name of the config file (without .json extension).
            module (str, optional): If specified, loads from the module folder.

        Returns:
            dict: The loaded configuration dictionary.
        """
        config_file = ConfigManager._get_config_path(config_name, module)

        # Use per-file lock
        with ConfigManager._get_lock(config_file):
            if config_file in ConfigManager._loaded_configs:
                return ConfigManager._loaded_configs[config_file]

            if not os.path.exists(config_file):
                logger.error(f"Config file {config_file} not found.")
                return {}

            try:
                with open(config_file, "r") as file:
                    data = json.load(file)
                    ConfigManager._loaded_configs[config_file] = data
                    logger.info(f"Loaded config: {config_file}")
                    return data
            except Exception as e:
                logger.error(f"Failed to load {config_file}: {e}")
                return {}

    @staticmethod
    def get(config_name: str, key: str, default=None, module: str = None):
        """
        Get a specific config value from a configuration file in a thread-safe way.

        Args:
            config_name (str): The name of the config file (without .json extension).
            key (str): The key to retrieve.
            default: The default value if key is not found.
            module (str, optional): If specified, loads from the module folder.

        Returns:
            Any: The retrieved config value or default.
        """
        config = ConfigManager.load_config(config_name, module)
        return config.get(key, default)

    @staticmethod
    def set(config_name: str, key: str, value, module: str = None):
        """
        Modify a config value in memory in a thread-safe way.

        Args:
            config_name (str): The name of the config file (without .json extension).
            key (str): The key to update.
            value: The new value to set.
            module (str, optional): If specified, updates in the module folder.
        """
        config_file = ConfigManager._get_config_path(config_name, module)

        with ConfigManager._get_lock(config_file):
            if config_file not in ConfigManager._loaded_configs:
                ConfigManager.load_config(config_name, module)

            ConfigManager._loaded_configs[config_file][key] = value
            logger.info(f"Updated config: {config_name} -> {key}: {value}")

    @staticmethod
    def save(config_name: str, module: str = None):
        """
        Save the updated config back to its JSON file in a thread-safe way.

        Args:
            config_name (str): The name of the config file (without .json extension).
            module (str, optional): If specified, saves in the module folder.
        """
        config_file = ConfigManager._get_config_path(config_name, module)

        with ConfigManager._get_lock(config_file):
            if config_file not in ConfigManager._loaded_configs:
                logger.error(f"Cannot save {config_name}. It was not loaded.")
                return

            try:
                with open(config_file, "w") as file:
                    json.dump(ConfigManager._loaded_configs[config_file], file, indent=4)
                    logger.info(f"Saved config: {config_file}")
            except Exception as e:
                logger.error(f"Failed to save {config_file}: {e}")
