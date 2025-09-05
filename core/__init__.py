import yaml
from pathlib import Path

settings_path = Path("config/settings.yaml")

with open(settings_path, "r") as f:
    settings = yaml.safe_load(f) or {}

debug_mode: bool = settings.get("cloud", {}).get("debug_mode", False)
autoregister: bool = settings.get("cloud", {}).get("autoregister", True)
use_https: bool = settings.get("network", {}).get("use_https", True)
server_path: str = settings.get("server", {}).get("default_path", "../Cloud/running/static")
heartbeat_delay: int = settings.get("server", {}).get("heartbeat_delay", 10)
cert_days: int = settings.get("network", {}).get("cert_duration_days", 365)
autocert: bool = settings.get("network", {}).get("auto_cert", False)
host: str = settings.get("cloud", {}).get("host", "localhost")
port: int = settings.get("cloud", {}).get("port", 9989)
auth_config_path: str = settings.get("network", {}).get("auth_config_path", "config/auth_tokens.yaml")
cert_file_path: Path = Path(settings.get("network", {}).get("cert_file_path", "./config/cert.pem"))
key_file_path: Path = Path(settings.get("network", {}).get("key_file_path", "./config/key.pem"))
auto_api: bool = settings.get("network", {}).get("auto_api", False)
communication_type: str = settings.get("network", {}).get("communication_type", "websocket").lower()
redis_channel: str = settings.get("network", {}).get("redis_channel", "echocloud:all")
redis_password: str = settings.get("network", {}).get("redis_password", "password")
redis_user: str = settings.get("network", {}).get("redis_user", "default")

storage_type: str = settings.get("storage", {}).get("storage_type", "h2")
storage_host: str = settings.get("storage", {}).get("host", "localhost")
storage_port: int = settings.get("storage", {}).get("port", 3306)
storage_username: str = settings.get("storage", {}).get("username", "username")
storage_password: str = settings.get("storage", {}).get("password", "password")
storage_database: str = settings.get("storage", {}).get("database", "EchoCloud")
storage_table_name: str = settings.get("storage", {}).get("table_name", "json_storage")
storage_h2_file_path: str = settings.get("storage", {}).get("h2_file_path", "../data/")



def get_section(section: str, key: str, default=None):
    return settings.get(section, {}).get(key, default)

