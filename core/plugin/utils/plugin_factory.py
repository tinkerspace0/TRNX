import os
import json
import shutil
import importlib
import inspect
import re
from typing import Tuple
from core.plugin.plugin_base import Plugin

def to_camel_case(s: str) -> str:
    """Convert a snake_case or lowercase string to CamelCase."""
    return ''.join(word.capitalize() for word in s.split('_'))

def camel_to_snake(name: str) -> str:
    """Convert a CamelCase string to snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def search_plugin_type(plugin_type: str) -> Tuple[str, str]:
    """
    Search through all modules in core/plugin/types for a class whose name matches plugin_type.
    Returns a tuple (module_name, base_class_name) if found.
    Raises an ImportError if not found.
    """
    types_dir = os.path.join(os.path.dirname(__file__), "..", "types")
    for fname in os.listdir(types_dir):
        if fname.endswith(".py") and fname != "__init__.py":
            module_name = os.path.splitext(fname)[0]
            full_module_name = f"core.plugin.types.{module_name}"
            try:
                module = importlib.import_module(full_module_name)
            except ImportError:
                continue
            for name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                # Only consider classes defined in this module.
                if cls.__module__ == full_module_name and issubclass(cls, Plugin) and cls is not Plugin:
                    if name.lower() == plugin_type.lower():
                        return full_module_name, name
    raise ImportError(f"No plugin type '{plugin_type}' found in core/plugin/types.")

def generate_template_from_base(plugin_name: str, plugin_type: str) -> str:
    """
    Dynamically generate a class template that inherits from a base class.
    The plugin_type is expected to be the class name (e.g. "ExchangeInterface" or "Indicator").
    This function searches the modules in core/plugin/types for the class.
    Returns the generated code as a string.
    """
    # If the plugin_type contains a dot, assume it's in the form "module.ClassName".
    if '.' in plugin_type:
        module_part, class_part = plugin_type.split('.', 1)
        module_name = f"core.plugin.types.{module_part.lower()}"
        base_class_name = class_part
    else:
        # Search for the plugin_type among all available types.
        module_name, base_class_name = search_plugin_type(plugin_type)
    
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}'. Make sure it exists.") from e
    
    try:
        base_class = getattr(module, base_class_name)
    except AttributeError as e:
        raise AttributeError(f"Module '{module_name}' has no attribute '{base_class_name}'.") from e

    # Use inspect to get all abstract methods from the base class.
    abstract_methods = []
    for name, member in inspect.getmembers(base_class, predicate=inspect.isfunction):
        if getattr(member, '__isabstractmethod__', False):
            abstract_methods.append((name, inspect.signature(member)))
    
    lines = []
    # Import statement for the base class.
    lines.append(f"from {module_name} import {base_class_name}")
    lines.append("from core.debug.logger import logger")
    lines.append("")
    # Class definition.
    class_name = to_camel_case(plugin_name)
    lines.append(f"class {class_name}({base_class_name}):")
    if abstract_methods:
        for method_name, sig in abstract_methods:
            lines.append(f"    def {method_name}{sig}:")
            lines.append(f"        logger.info('Executing {method_name} in {class_name}')")
            lines.append("        # TODO: implement this method")
            lines.append("        pass")
            lines.append("")
    else:
        lines.append("    pass")
    
    return "\n".join(lines)

def create_template(plugin_name: str, plugin_type: str, output_dir: str) -> str:
    """
    Create a plugin template folder dynamically based on the specified plugin type.
    The plugin_type is a class name (e.g. "ExchangeInterface" or "Indicator").
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
    # Main plugin file.
    plugin_main_file = os.path.join(plugin_folder, f"{plugin_name}.py")

    # Create the plugin_manifest.json with metadata.
    manifest = {
        "name": plugin_name,
        "version": "0.1",
        "description": f"Template for a plugin of type {plugin_type}.",
        "entry_point": f"{plugin_name}.{plugin_name}:{class_name}",
        "author": "",
        "license": "MIT",
        "dependencies": []
    }
    manifest_path = os.path.join(plugin_folder, "plugin_manifest.json")
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=4)

    # Dynamically generate the main plugin code from the base class.
    main_code = generate_template_from_base(plugin_name, plugin_type)
    
    with open(plugin_main_file, "w") as f:
        f.write(main_code)
    
    print(f"Plugin template created at: {plugin_folder}")
    return plugin_folder

def package_plugin(plugin_folder: str, output_folder: str = None) -> str:
    """
    Package a plugin template folder into a .plg file.
    Returns the path to the generated .plg file.
    
    If output_folder is not provided, the package will be stored in core/plugin/plugins.
    """
    if not os.path.exists(plugin_folder):
        raise FileNotFoundError(f"Plugin folder '{plugin_folder}' does not exist.")
    
    # Determine output folder.
    if output_folder is None:
        output_folder = os.path.join(os.getcwd(), "core", "plugin", "plugins")
    os.makedirs(output_folder, exist_ok=True)
    
    base_name = os.path.basename(plugin_folder)
    plg_filename = os.path.join(output_folder, f"{base_name}.plg")
    
    parent_dir = os.path.dirname(plugin_folder)
    shutil.make_archive(plg_filename[:-4], 'zip', root_dir=parent_dir, base_dir=base_name)
    
    print(f"Plugin packaged as: {plg_filename}")
    return plg_filename

def get_available_plugin_types() -> list:
    """
    Scan the core/plugin/types folder and return a list of available plugin type names.
    Only returns the names of the classes (without module paths) that are subclasses of Plugin.
    """
    import importlib
    import inspect
    available_types = set()
    types_dir = os.path.join(os.path.dirname(__file__), "..", "types")
    if os.path.exists(types_dir):
        for fname in os.listdir(types_dir):
            if fname.endswith(".py") and fname != "__init__.py":
                module_name = os.path.splitext(fname)[0]
                full_module_name = f"core.plugin.types.{module_name}"
                try:
                    module = importlib.import_module(full_module_name)
                except ImportError as e:
                    print(f"Error importing module {full_module_name}: {e}")
                    continue
                for name, cls in inspect.getmembers(module, predicate=inspect.isclass):
                    # Only include classes defined in this module that are subclasses of Plugin.
                    if cls.__module__ == full_module_name and issubclass(cls, Plugin) and cls is not Plugin:
                        available_types.add(name)
    else:
        print(f"Types directory not found: {types_dir}")
    return sorted(list(available_types))
