import yaml

from servers.linux import LinuxServerManager


class ServerManager:
    def __init__(self, settings_path="config/settings.yaml"):
        with open(settings_path, "r") as f:
            self.settings = yaml.safe_load(f)
        self.base_path = self.settings["default_server_path"]
        self.server_version = self.settings["server_version"]

    def load_server_config(self, config_path):
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def start_server(self, config_path):
        config = self.load_server_config(config_path)
        linux_manager = LinuxServerManager(config, self.base_path, self.server_version)
        return linux_manager.start_server()

    def stop_server(self, config_path):
        config = self.load_server_config(config_path)
        linux_manager = LinuxServerManager(config, self.base_path, self.server_version)
        return linux_manager.stop_server()
