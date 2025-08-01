from datetime import datetime
from typing import List, Dict, Optional

import yaml
from pathlib import Path

from core.console import pError, pWarning, pInfo
from servers.linux import LinuxServerManager

from core import settings



class ServerManager:
    def __init__(self, settings_path="config/settings.yaml", server_config_dir="data/server_configs"):

        #Settings von Initializer Benutzen
        self.settings = settings

        self.base_path: str = self.settings["default_server_path"]
        self.server_version: str = self.settings["server_version"]
        self.settings_path: str = settings_path
        self.server_config_dir: Path = Path(server_config_dir)
        self.servers: List[Server] = []

        self.autoregister()

    def load_server_config(self, config_path: Path) -> Dict:
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

    def autoregister(self):
        if not self.server_config_dir.exists():
            pWarning(f"Config-Verzeichnis {self.server_config_dir} existiert nicht.")
            return

        configs = list(self.server_config_dir.glob("*.yml"))
        if not configs:
            pInfo("Keine Server-Konfigurationen gefunden.")
            return

        for cfg_path in configs:
            cfg = self.load_server_config(cfg_path)
            server_id = cfg_path.stem

            server = Server(
                server_id=server_id,
                name=cfg.get("server_name", server_id),
                ip=cfg.get("ip", "127.0.0.1"),
                port=int(cfg.get("port", 25565)),
                server_type=cfg.get("server_type", "Unknown"),
                config_path=str(cfg_path),
                java_memory=cfg.get("java_memory", {"Xmx": "1024M", "Xms": "1024M"})
            )
            self.servers.append(server)
            pInfo(f"Server '{server.name}' registriert.")

    def get_server_by_id(self, server_id: str) -> Optional['Server']:
        return next((s for s in self.servers if s.server_id == server_id), None)

    def list_servers(self) -> List[str]:
        return [s.name for s in self.servers]

    def start_server(self, config_path: str):
        config = self.load_server_config(Path(config_path))
        linux_manager = LinuxServerManager(config, self.base_path, self.server_version)
        return linux_manager.start_server()

    def stop_server(self, config_path: str):
        config = self.load_server_config(Path(config_path))
        linux_manager = LinuxServerManager(config, self.base_path, self.server_version)
        return linux_manager.stop_server()

class Server:
    def __init__(
        self,
        server_id: str,
        name: str,
        ip: str,
        port: int,
        server_type: str,
        config_path: str,
        java_memory: Optional[Dict[str, str]] = None,
    ):
        self.server_id: str = server_id
        self.name: str = name
        self.ip: str = ip
        self.port: int = port
        self.server_type: str = server_type
        self.config_path: str = config_path

        # Java Memory Optionen aus YAML
        self.java_memory: Dict[str, str] = java_memory or {
            "Xmx": "1024M",
            "Xms": "1024M"
        }

        # Laufzeitinfos
        self.is_running: bool = False
        self.start_time: Optional[datetime] = None
        self.tps: Optional[float] = None
        self.cpu_usage: Optional[float] = None
        self.ram_usage_mb: Optional[float] = None

        # Spieler & Plugins
        self.players_online: List[str] = []
        self.max_players: int = 0
        self.plugins: List[str] = []
        self.server_properties: Dict[str, str] = {}

        # Linux
        self.process_id: Optional[int] = None
        self.last_output_lines: List[str] = []

    def start(self):
        self.is_running = True
        self.start_time = datetime.now()
        pInfo(f"[INFO] Server '{self.name}' wurde gestartet.")

    def stop(self):
        self.is_running = False
        self.start_time = None
        pInfo(f"[INFO] Server '{self.name}' wurde gestoppt.")

    def update_metrics(self, tps: float, cpu_usage: float, ram_usage: float):
        self.tps = round(tps, 2)
        self.cpu_usage = round(cpu_usage, 2)
        self.ram_usage_mb = round(ram_usage, 2)

    def update_players(self, players: List[str], max_players: int):
        self.players_online = players
        self.max_players = max_players

    def update_plugins(self, plugins: List[str]):
        self.plugins = plugins

    def update_server_properties(self, properties: Dict[str, str]):
        self.server_properties = properties

    def get_uptime(self) -> Optional[str]:
        if self.start_time and self.is_running:
            delta = datetime.now() - self.start_time
            return str(delta).split(".")[0]
        return None

    def summary(self) -> Dict[str, any]:
        return {
            "Name": self.name,
            "Typ": self.server_type,
            "IP": f"{self.ip}:{self.port}",
            "Status": "Online" if self.is_running else "Offline",
            "TPS": self.tps,
            "CPU": f"{self.cpu_usage}%",
            "RAM": f"{self.ram_usage_mb} MB",
            "Spieler": f"{len(self.players_online)}/{self.max_players}",
            "Plugins": self.plugins,
            "Java RAM": f"Xmx: {self.java_memory.get('Xmx')} | Xms: {self.java_memory.get('Xms')}",
            "Laufzeit": self.get_uptime(),
        }

    def get_status(self):
        status = "Online" if self.is_running else "Offline"
        status_color = "green" if self.is_running else "red"
        status_symbol = "🟢" if self.is_running else "🔴"

        ram = f"{self.ram_usage_mb} MB" if self.ram_usage_mb is not None else "?"
        cpu = f"{self.cpu_usage}%" if self.cpu_usage is not None else "?"
        tps = f"{self.tps}" if self.tps is not None else "?"
        players = f"{len(self.players_online)}/{self.max_players}"
        plugins = ', '.join(self.plugins) if self.plugins else "Keine"
        uptime = self.get_uptime() or "–"

        java_ram = f"Xmx: {self.java_memory.get('Xmx')} | Xms: {self.java_memory.get('Xms')}"

        lines = [
            "[cyan bold]╭────────────────  Server Status ─────────────────╮[/cyan bold]",
            f"[cyan]│[/cyan] [bold white]Name:[/bold white]      {self.name}",
            f"[cyan]│[/cyan] [bold white]Typ:[/bold white]       {self.server_type}",
            f"[cyan]│[/cyan] [bold white]IP:[/bold white]        {self.ip}:{self.port}",
            f"[cyan]│[/cyan] [bold white]Status:[/bold white]    [{status_color}]{status_symbol} {status}[/{status_color}]",
            f"[cyan]│[/cyan] [bold white]TPS:[/bold white]       {tps}",
            f"[cyan]│[/cyan] [bold white]CPU:[/bold white]       {cpu}",
            f"[cyan]│[/cyan] [bold white]RAM:[/bold white]       {ram}",
            f"[cyan]│[/cyan] [bold white]Spieler:[/bold white]   {players}",
            f"[cyan]│[/cyan] [bold white]Plugins:[/bold white]   {plugins}",
            f"[cyan]│[/cyan] [bold white]Java RAM:[/bold white]  {java_ram}",
            f"[cyan]│[/cyan] [bold white]Uptime:[/bold white]    {uptime}",
            "[cyan bold]╰──────────────────────────────────────────────────╯[/cyan bold]"
        ]

        pInfo(" ")
        for line in lines:
            pInfo(f"[blue][[/blue][green]*[/green][blue]][/blue] {line}")
        pInfo(" ")

