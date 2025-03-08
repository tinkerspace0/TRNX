# core/plugin/plugin_factory.py
import os
import json
import shutil
import zipfile

def to_camel_case(s: str) -> str:
    """Convert a snake_case or lowercase string to CamelCase."""
    return ''.join(word.capitalize() for word in s.split('_'))

def create_template(plugin_name: str, plugin_type: str, output_dir: str) -> str:
    """
    Create a plugin template folder with the necessary files.
    Returns the path to the created plugin template folder.
    """
    # Create the plugin folder.
    plugin_folder = os.path.join(output_dir, plugin_name)
    os.makedirs(plugin_folder, exist_ok=True)

    # Create an empty __init__.py.
    init_path = os.path.join(plugin_folder, "__init__.py")
    with open(init_path, "w") as f:
        f.write(f"# {plugin_name} package initializer\n")

    # Create a requirements.txt file for plugin-specific dependencies.
    requirements_path = os.path.join(plugin_folder, "requirements.txt")
    with open(requirements_path, "w") as f:
        f.write("# Add plugin-specific dependencies here\n")

    # Determine the class name from the plugin name.
    class_name = to_camel_case(plugin_name)
    # Main plugin file (e.g. my_plugin.py).
    plugin_main_file = os.path.join(plugin_folder, f"{plugin_name}.py")

    # Create the plugin_manifest.json with metadata.
    manifest = {
        "name": plugin_name,
        "version": "0.1",
        "description": f"Template for a plugin of type {plugin_type}.",
        "entry_point": f"{plugin_name}.{plugin_name}:{class_name}",
        "author": "",
        "license": "MIT",
        "dependencies": []  # List any required packages for this plugin
    }
    manifest_path = os.path.join(plugin_folder, "plugin_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    # Generate the main code based on plugin type.
    if plugin_type.lower() == "exchangeinterface":
        main_code = f'''\
from core.plugin import ExchangeInterface
from core.debug.logger import logger

class {class_name}(ExchangeInterface):
    def _define_inputs(self) -> None:
        # Define required input ports (if any).
        self._required_inputs = {{}}

    def _define_outputs(self) -> None:
        # Define provided output ports.
        self._provided_outputs = {{"ticker": ((2,), float)}}

    def fetch_ticker(self, symbol: str) -> None:
        logger.info(f"Fetching ticker for {{symbol}}")
        # Write ticker data to shared memory, e.g.:
        # self._outputs['ticker'].write(data)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 100) -> None:
        logger.info(f"Fetching OHLCV for {{symbol}}")
        # Write OHLCV data to shared memory

    def fetch_recent_trades(self, symbol: str, limit: int = 20) -> None:
        logger.info(f"Fetching recent trades for {{symbol}}")
        # Write recent trades data to shared memory

    def fetch_order_book(self, symbol: str, depth: int = 10) -> None:
        logger.info(f"Fetching order book for {{symbol}}")
        # Write order book data to shared memory

    def fetch_market_status(self) -> None:
        logger.info("Fetching market status")
        # Write market status to shared memory

    def fetch_24h_volume(self, symbol: str) -> None:
        logger.info(f"Fetching 24h volume for {{symbol}}")
        # Write 24h volume data to shared memory
'''
    elif plugin_type.lower() == "dataprocessor":
        main_code = f'''\
from core.plugin.plugin_base import Plugin
from core.debug.logger import logger

class {class_name}(Plugin):
    def _define_inputs(self) -> None:
        # Define required input ports.
        self._required_inputs = {{}}

    def _define_outputs(self) -> None:
        # Define provided output ports.
        self._provided_outputs = {{}}

    def build(self) -> None:
        logger.info(f"{{self.__class__.__name__}} build complete.")

    def process(self) -> None:
        logger.info(f"{{self.__class__.__name__}} processing data.")
'''
    else:
        # Default template: basic plugin extending Plugin.
        main_code = f'''\
from core.plugin.plugin_base import Plugin
from core.debug.logger import logger

class {class_name}(Plugin):
    def _define_inputs(self) -> None:
        # Define required input ports.
        self._required_inputs = {{}}

    def _define_outputs(self) -> None:
        # Define provided output ports.
        self._provided_outputs = {{}}

    def build(self) -> None:
        logger.info(f"{{self.__class__.__name__}} build complete.")

    def process(self) -> None:
        logger.info(f"{{self.__class__.__name__}} processing data.")
'''

    with open(plugin_main_file, "w") as f:
        f.write(main_code)

    print(f"Plugin template created at: {plugin_folder}")
    return plugin_folder

def package_plugin(plugin_folder: str) -> str:
    """
    Package a plugin template folder into a .plg file.
    Returns the path to the generated .plg file.
    """
    if not os.path.exists(plugin_folder):
        raise FileNotFoundError(f"Plugin folder '{plugin_folder}' does not exist.")

    # Ensure the plugins directory exists
    plugins_dir = os.path.join(os.getcwd(), "plugins")
    os.makedirs(plugins_dir, exist_ok=True)

    base_name = os.path.basename(plugin_folder)  # e.g. "Binance"
    plg_filename = os.path.join(plugins_dir, f"{base_name}.plg")

    # Set the parent directory as root and base_dir as the plugin folder name.
    parent_dir = os.path.dirname(plugin_folder)
    # This creates an archive that, when extracted, will contain a folder "Binance" with the plugin files.
    shutil.make_archive(plg_filename[:-4], 'zip', root_dir=parent_dir, base_dir=base_name)

    print(f"Plugin packaged as: {plg_filename}")
    return plg_filename