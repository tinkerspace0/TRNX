# plugin_loader.py
import os
import zipfile
import tempfile
import importlib.util
import sys
import json
from core.debug.logger import logger
from core.plugin.plugin_base import Plugin


def load_plugin(plg_path: str) -> Plugin:
    """
    Load a plugin from a .plg file.
    """
    temp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(plg_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    # Try to locate plugin_manifest.json at the root.
    manifest_path = os.path.join(temp_dir, "plugin_manifest.json")
    if not os.path.exists(manifest_path):
        # If not found, check if there's a single directory in temp_dir.
        items = os.listdir(temp_dir)
        if len(items) == 1 and os.path.isdir(os.path.join(temp_dir, items[0])):
            base_dir = os.path.join(temp_dir, items[0])
            manifest_path = os.path.join(base_dir, "plugin_manifest.json")
        else:
            raise FileNotFoundError("plugin_manifest.json not found in archive.")
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    entry_point = manifest.get("entry_point")
    if not entry_point:
        raise ValueError("Plugin manifest missing entry_point.")
    
    module_name, class_name = entry_point.split(":")
    # Build module path relative to the extraction directory.
    module_path = os.path.join(temp_dir, *module_name.split(".")) + ".py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    
    plugin_class = getattr(module, class_name)
    if not issubclass(plugin_class, Plugin):
        raise TypeError("Loaded class does not extend Plugin base class.")
    
    plugin_instance = plugin_class()
    # Record the source .plg file for export purposes.
    plugin_instance._source_path = plg_path
    logger.info(f"Loaded plugin {plugin_class.__name__} from {plg_path}")
    return plugin_instance

def load_plugins(plugin_directory: str):
    """
    Load all .plg files from the given directory.
    Returns a list of plugin instances.
    """
    plugins = []
    for filename in os.listdir(plugin_directory):
        if filename.endswith(".plg"):
            plg_path = os.path.join(plugin_directory, filename)
            try:
                plugin_instance = load_plugin(plg_path)
                plugins.append(plugin_instance)
            except Exception as e:
                logger.error(f"Error loading plugin from {plg_path}: {e}")
    return plugins
