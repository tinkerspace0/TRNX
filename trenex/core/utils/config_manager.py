import json
import os
import threading
from core.debug.logger import logger

class ConfigManager:
    """Generalized ConfigManager that loads, modifies, and saves config files dynamically with per-file locks."""

    _loaded_configs = {}  # Stores in-memory modifications of config files
    _locks = {}  # Thread locks per config file

    @staticmethod
    def _validate_json_file(config_path: str):
        """Ensure that the file has a .json extension."""
        if not config_path.endswith(".json"):
            raise ValueError(f"Invalid file format: {config_path}. Only JSON files are allowed.")

    @staticmethod
    def _get_lock(config_path: str):
        """Retrieve or create a lock for a specific config file."""
        if config_path not in ConfigManager._locks:
            ConfigManager._locks[config_path] = threading.Lock()
        return ConfigManager._locks[config_path]

    @staticmethod
    def load_config(config_path: str):
        """
        Load a JSON config file dynamically in a thread-safe way.

        Args:
            config_path (str): Absolute or relative path to the config file.

        Returns:
            dict: The loaded configuration dictionary.
        """
        config_path = os.path.abspath(config_path)  # Normalize to absolute path
        ConfigManager._validate_json_file(config_path)  # Ensure it's a JSON file

        with ConfigManager._get_lock(config_path):
            if config_path in ConfigManager._loaded_configs:
                return ConfigManager._loaded_configs[config_path]

            if not os.path.exists(config_path):
                logger.error(f"Config file {config_path} not found.")
                return {}

            try:
                with open(config_path, "r") as file:
                    data = json.load(file)
                    ConfigManager._loaded_configs[config_path] = data
                    logger.info(f"Loaded config: {config_path}")
                    return data
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON format in {config_path}.")
            except Exception as e:
                logger.error(f"Failed to load {config_path}: {e}")

            return {}

    @staticmethod
    def get(config_path: str, key: str, default=None):
        """
        Get a specific config value from a configuration file in a thread-safe way.

        Args:
            config_path (str): Path to the config file.
            key (str): The key to retrieve.
            default: The default value if key is not found.

        Returns:
            Any: The retrieved config value or default.
        """
        config = ConfigManager.load_config(config_path)
        return config.get(key, default)

    @staticmethod
    def set(config_path: str, key: str, value):
        """
        Modify a config value in memory in a thread-safe way.

        Args:
            config_path (str): Path to the config file.
            key (str): The key to update.
            value: The new value to set.
        """
        config_path = os.path.abspath(config_path)
        ConfigManager._validate_json_file(config_path)  # Ensure it's a JSON file

        with ConfigManager._get_lock(config_path):
            if config_path not in ConfigManager._loaded_configs:
                ConfigManager.load_config(config_path)

            ConfigManager._loaded_configs[config_path][key] = value
            logger.info(f"Updated config: {config_path} -> {key}: {value}")

    @staticmethod
    def save(config_path: str):
        """
        Save the updated config back to its JSON file in a thread-safe way.

        Args:
            config_path (str): Path to the config file.
        """
        config_path = os.path.abspath(config_path)
        ConfigManager._validate_json_file(config_path)  # Ensure it's a JSON file

        with ConfigManager._get_lock(config_path):
            if config_path not in ConfigManager._loaded_configs:
                logger.error(f"Cannot save {config_path}. It was not loaded.")
                return

            try:
                with open(config_path, "w") as file:
                    json.dump(ConfigManager._loaded_configs[config_path], file, indent=4)
                    logger.info(f"Saved config: {config_path}")
            except Exception as e:
                logger.error(f"Failed to save {config_path}: {e}")
