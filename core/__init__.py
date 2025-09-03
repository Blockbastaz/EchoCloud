import yaml
from pathlib import Path

settings_path = Path("config/settings.yaml")

with open(settings_path, "r") as f:
    settings = yaml.safe_load(f) or {}

debug_mode: bool = settings.get("cloud", {}).get("debug_mode", False)
autoregister: bool = settings.get("cloud", {}).get("autoregister", True)
use_https: bool = settings.get("network", {}).get("use_https", True)
server_path: str = settings.get("server", {}).get("default_path", "../Cloud/running/static")
cert_days: int = settings.get("network", {}).get("cert_duration_days", 365)
autocert: bool = settings.get("network", {}).get("auto_cert", False)
host: str = settings.get("network", {}).get("host", "localhost")
port: int = settings.get("network", {}).get("port", 9989)
auth_config_path: str = settings.get("network", {}).get("auth_config_path", "config/auth_tokens.yaml")
cert_file_path: Path = Path(settings.get("network", {}).get("cert_file_path", "./config/cert.pem"))
key_file_path: Path = Path(settings.get("network", {}).get("key_file_path", "./config/key.pem"))
auto_api: bool = settings.get("network", {}).get("auto_api", False)

def get_section(section: str, key: str, default=None):
    return settings.get(section, {}).get(key, default)

