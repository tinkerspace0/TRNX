import os
import json
import shutil
import importlib
import inspect

def to_camel_case(s: str) -> str:
    """Convert a snake_case or lowercase string to CamelCase."""
    return ''.join(word.capitalize() for word in s.split('_'))

def generate_template_from_base(plugin_name: str, plugin_type: str) -> str:
    """
    Dynamically generate a class template that inherits from a base class.
    The plugin_type should match a module in core.plugin.types and the base
    class name is assumed to be the CamelCase version of plugin_type.
    Returns the generated code as a string.
    """
    module_name = f"core.plugin.types.{plugin_type.lower()}"
    base_class_name = to_camel_case(plugin_type)
    
    try:
        module = importlib.import_module(module_name)
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_name}'. Make sure it exists.") from e
    
    try:
        base_class = getattr(module, base_class_name)
    except AttributeError as e:
        raise AttributeError(f"Module '{module_name}' has no attribute '{base_class_name}'.") from e

    # Use inspect to get all abstract methods (or all public methods) from the base class.
    abstract_methods = []
    for name, member in inspect.getmembers(base_class, predicate=inspect.isfunction):
        if getattr(member, '__isabstractmethod__', False):
            abstract_methods.append((name, inspect.signature(member)))
    
    # Build the class template code.
    lines = []
    # Import statements.
    lines.append(f"from core.plugin.types.{plugin_type.lower()} import {base_class_name}")
    lines.append("from core.debug.logger import logger")
    lines.append("")
    # Class definition.
    class_name = to_camel_case(plugin_name)
    lines.append(f"class {class_name}({base_class_name}):")
    if abstract_methods:
        for method_name, sig in abstract_methods:
            # Remove 'self' from the signature for a cleaner output if desired.
            # Alternatively, simply use the full signature.
            lines.append(f"    def {method_name}{sig}:")
            lines.append(f"        logger.info('Executing {method_name} in {class_name}')")
            lines.append("        # TODO: implement this method")
            lines.append("        pass")
            lines.append("")
    else:
        # If no abstract methods were found, just leave a pass.
        lines.append("    pass")
    
    return "\n".join(lines)

def create_template(plugin_name: str, plugin_type: str, output_dir: str) -> str:
    """
    Create a plugin template folder dynamically based on the base class.
    This function uses the base class in core/plugin/types to generate a template.
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
    # Main plugin file (e.g., my_plugin.py).
    plugin_main_file = os.path.join(plugin_folder, f"{plugin_name}.py")

    # Create the plugin_manifest.json with metadata.
    manifest = {
        "name": plugin_name,
        "version": "0.1",
        "description": f"Template for a plugin of type {plugin_type}.",
        "entry_point": f"{plugin_name}.{plugin_name}:{class_name}",
        "author": "",
        "license": "MIT",
        "dependencies": []  # List any required packages for this plugin.
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

def package_plugin(plugin_folder: str) -> str:
    """
    Package a plugin template folder into a .plg file.
    Returns the path to the generated .plg file.
    """
    if not os.path.exists(plugin_folder):
        raise FileNotFoundError(f"Plugin folder '{plugin_folder}' does not exist.")
    
    # Ensure the plugins directory exists.
    plugins_dir = os.path.join(os.getcwd(), "plugins")
    os.makedirs(plugins_dir, exist_ok=True)
    
    base_name = os.path.basename(plugin_folder)  # e.g., "Binance"
    plg_filename = os.path.join(plugins_dir, f"{base_name}.plg")
    
    # Package the plugin folder as a zip archive that retains the folder structure.
    parent_dir = os.path.dirname(plugin_folder)
    shutil.make_archive(plg_filename[:-4], 'zip', root_dir=parent_dir, base_dir=base_name)
    
    print(f"Plugin packaged as: {plg_filename}")
    return plg_filename
