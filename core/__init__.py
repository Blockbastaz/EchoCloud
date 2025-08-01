import yaml
from pathlib import Path

settings_path: Path = Path("config/settings.yaml")
settings: str = ""
with open(settings_path, "r") as f:
    settings: str = yaml.safe_load(f)

global debugMode
debugMode: bool = settings.get("debug_mode", False)

autoregister: bool = settings.get("autoregister", True)