from servers.linux import LinuxServer
import yaml
import os

CONFIG_DIR = "data/server_configs"

def load_server_config(name: str) -> dict:
    path = os.path.join(CONFIG_DIR, f"{name}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Server config not found: {name}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

def start_server(name: str):
    config = load_server_config(name)
    server = LinuxServer(config)
    return server.start()

def stop_server(name: str):
    config = load_server_config(name)
    server = LinuxServer(config)
    return server.stop()
