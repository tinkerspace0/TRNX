import argparse
import requests
import os
import subprocess
import time
import signal
import sys

# Default API address
API_HOST = "127.0.0.1"
API_PORT = 8000
API_URL = f"http://{API_HOST}:{API_PORT}"

# Process ID for the API server
api_process = None

# -----------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------
def wait_for_api(timeout=30):
    """Wait until the API is available, or timeout after a given number of seconds."""
    import time
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{API_URL}/docs", timeout=2)
            if response.status_code == 200:
                print(f"✅ API is ready at {API_URL}")
                return True
        except requests.exceptions.RequestException:
            time.sleep(0.5)
    return False

def start_api_server():
    """Start the Trenex API server if not already running."""
    global api_process

    try:
        response = requests.get(f"{API_URL}/docs", timeout=2)
        if response.status_code == 200:
            print(f"✅ Trenex API is already running at {API_URL}")
            return
    except requests.ConnectionError:
        pass  # Server is not running

    print("🚀 Starting Trenex API server...")
    
    api_process = subprocess.Popen(
        ["uvicorn", "api.api:app", "--host", API_HOST, "--port", str(API_PORT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    
    if wait_for_api(timeout=10):
        print(f"✅ Trenex API started at {API_URL}")
    else:
        print("❌ Failed to start API within timeout.")
        sys.exit(1)
def stop_api_server():
    """Stop the Trenex API server when the CLI exits."""
    global api_process
    if api_process:
        print("🛑 Stopping Trenex API server...")
        api_process.terminate()
        api_process.wait()
        print("✅ Trenex API stopped.")

def send_post_request(endpoint, data=None):
    """Send a POST request to the Trenex API."""
    url = f"{API_URL}{endpoint}"
    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def open_in_vscode(path):
    """Open the specified path in VS Code."""
    if sys.platform.startswith("win"):
        os.system(f"code {path}")
    else:
        subprocess.run(["code", path])

# -----------------------------------------------------------
# CLI Commands
# -----------------------------------------------------------
def create_plugin_template(name, plugin_type, open_vscode=False):
    """Create a new plugin template via the Trenex API."""
    print(f"🛠 Creating plugin template '{name}' of type '{plugin_type}'...")
    response = send_post_request("/plugin/template", {"plugin_name": name, "plugin_type": plugin_type})
    
    path = response.get("template_path")
    print(f"✅ Plugin template created at: {path}")

    if open_vscode:
        print("📂 Opening in VS Code...")
        open_in_vscode(path)

def package_plugin(folder):
    """Package a plugin into a .plg file."""
    print(f"📦 Packaging plugin in '{folder}'...")
    response = send_post_request("/plugin/package", {"plugin_folder": folder})
    
    plg_path = response.get("plg_path")
    print(f"✅ Plugin packaged: {plg_path}")

def start_bot(name):
    """Start a new bot (TRNX instance)."""
    print(f"🚀 Starting bot '{name}'...")
    response = send_post_request("/bot/start", {"name": name})
    print(response.get("message"))

def build_bot():
    """Build the active bot (wires plugins, computes execution order)."""
    print("🔧 Building bot...")
    response = send_post_request("/bot/build")
    print(response.get("message"))

def run_bot():
    """Run the active bot (execute loaded plugins in order)."""
    print("▶ Running bot...")
    response = send_post_request("/bot/run")
    print(response.get("message"))

# -----------------------------------------------------------
# CLI Argument Parsing
# -----------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(prog="trenex", description="Trenex CLI - Manage trading bots & plugins.")

    subparsers = parser.add_subparsers(dest="command")

    # Plugin Template Command
    plugin_parser = subparsers.add_parser("plugintemplate", help="Create a new plugin template")
    plugin_parser.add_argument("-n", "--name", required=True, help="Plugin name")
    plugin_parser.add_argument("-t", "--type", required=True, help="Plugin type (e.g., ExchangeInterface, DataProcessor)")
    plugin_parser.add_argument("--open", action="store_true", help="Open the template in VS Code after creation")

    # Package Plugin Command
    package_parser = subparsers.add_parser("package", help="Package a plugin into a .plg file")
    package_parser.add_argument("-f", "--folder", required=True, help="Path to the plugin folder")

    # Start Bot Command
    start_parser = subparsers.add_parser("startbot", help="Start a new bot")
    start_parser.add_argument("-n", "--name", required=True, help="Bot name")

    # Build Bot Command
    subparsers.add_parser("buildbot", help="Build the active bot")

    # Run Bot Command
    subparsers.add_parser("runbot", help="Run the active bot")

    args = parser.parse_args()

    # Start the API Server (if needed)
    start_api_server()

    # Handle CLI commands
    if args.command == "plugintemplate":
        create_plugin_template(args.name, args.type, args.open)
    elif args.command == "package":
        package_plugin(args.folder)
    elif args.command == "startbot":
        start_bot(args.name)
    elif args.command == "buildbot":
        build_bot()
    elif args.command == "runbot":
        run_bot()
    else:
        parser.print_help()

    # Stop the API server when the CLI exits
    stop_api_server()

# Gracefully handle CTRL+C
def signal_handler(sig, frame):
    stop_api_server()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    main()
