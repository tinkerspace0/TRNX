# core/utils/config_manager.py
import json
import os
import threading
from core.debug.logger import logger

class ConfigManager:
    _loaded_configs = {}
    _locks = {}

    @staticmethod
    def _validate_json_file(config_path: str):
        if not config_path.endswith(".json"):
            raise ValueError("Only JSON config files allowed.")

    @staticmethod
    def _get_lock(config_path: str):
        if config_path not in ConfigManager._locks:
            ConfigManager._locks[config_path] = threading.Lock()
        return ConfigManager._locks[config_path]

    @staticmethod
    def load_config(config_path: str):
        config_path = os.path.abspath(config_path)
        ConfigManager._validate_json_file(config_path)
        with ConfigManager._get_lock(config_path):
            if config_path in ConfigManager._loaded_configs:
                return ConfigManager._loaded_configs[config_path]
            if not os.path.exists(config_path):
                logger.error(f"Config file {config_path} not found.")
                return {}
            try:
                with open(config_path, "r") as f:
                    data = json.load(f)
                    ConfigManager._loaded_configs[config_path] = data
                    logger.info(f"Loaded config: {config_path}")
                    return data
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return {}

    @staticmethod
    def get(config_path: str, key: str, default=None):
        config = ConfigManager.load_config(config_path)
        return config.get(key, default)

    @staticmethod
    def set(config_path: str, key: str, value):
        config_path = os.path.abspath(config_path)
        ConfigManager._validate_json_file(config_path)
        with ConfigManager._get_lock(config_path):
            if config_path not in ConfigManager._loaded_configs:
                ConfigManager.load_config(config_path)
            ConfigManager._loaded_configs[config_path][key] = value
            logger.info(f"Set config {config_path}: {key} = {value}")

    @staticmethod
    def save(config_path: str):
        config_path = os.path.abspath(config_path)
        ConfigManager._validate_json_file(config_path)
        with ConfigManager._get_lock(config_path):
            if config_path not in ConfigManager._loaded_configs:
                logger.error(f"Cannot save; config not loaded: {config_path}")
                return
            try:
                with open(config_path, "w") as f:
                    json.dump(ConfigManager._loaded_configs[config_path], f, indent=4)
                    logger.info(f"Saved config: {config_path}")
            except Exception as e:
                logger.error(f"Error saving config: {e}")
