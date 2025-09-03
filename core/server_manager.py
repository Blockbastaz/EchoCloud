import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import yaml
from rich.prompt import Prompt

from core import settings, get_section
from core.console import pError, pWarning, pInfo


class ServerManager:
    def __init__(self, server_config_dir="./data/server_configs", ):

        #Settings von Initializer Benutzen
        self.settings = settings

        self.base_path: str = get_section("server", "default_path", "../Cloud/running/static")
        self.server_version: str = get_section("server", "version", "not found")
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

        configs = list(self.server_config_dir.glob("*.yaml"))
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


    #TODO Funktioniert Aktuell nur für Linux
    def scan_servers(self):
        base = Path(self.base_path)
        if not base.exists():
            pError(f"Base path {base} existiert nicht.")
            return

        pInfo(f"Scanne {base} nach Servern...")

        found_servers = []  # merken was wir gefunden haben

        for server_type_dir in base.iterdir():
            if not server_type_dir.is_dir():
                continue

            server_type = server_type_dir.name

            for server_dir in server_type_dir.iterdir():
                if not server_dir.is_dir():
                    continue

                run_sh = server_dir / "run.sh"
                server_properties = server_dir / "server.properties"

                if run_sh.exists() and server_properties.exists():
                    # Defaults
                    ip = "127.0.0.1"
                    port = 25565
                    java_memory = {"Xmx": "1024M", "Xms": "1024M"}

                    try:
                        with open(server_properties, "r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if line.startswith("server-ip="):
                                    ip_val = line.split("=", 1)[1].strip()
                                    if ip_val:
                                        ip = ip_val
                                elif line.startswith("server-port="):
                                    port_val = line.split("=", 1)[1].strip()
                                    if port_val.isdigit():
                                        port = int(port_val)
                    except Exception as e:
                        pWarning(f"Konnte {server_properties} nicht lesen: {e}")

                    try:
                        with open(run_sh, "r", encoding="utf-8") as f:
                            content = f.read()
                            match_xmx = re.search(r"-Xmx(\d+[MG]?)", content)
                            match_xms = re.search(r"-Xms(\d+[MG]?)", content)
                            if match_xmx:
                                java_memory["Xmx"] = match_xmx.group(1)
                            if match_xms:
                                java_memory["Xms"] = match_xms.group(1)
                    except Exception as e:
                        pWarning(f"Konnte {run_sh} nicht lesen: {e}")

                    server_id = server_dir.name
                    server = Server(
                        server_id=server_id,
                        name=server_id,
                        ip=ip,
                        port=port,
                        server_type=server_type,
                        config_path="__AUTO__",
                        java_memory=java_memory
                    )
                    server.run_sh_path = str(run_sh.resolve())

                    self.servers.append(server)
                    found_servers.append(server)
                    pInfo(
                        f"Gefunden: {server_type}/{server_id} "
                        f"(IP: {ip}, Port: {port}, RAM: Xmx={java_memory['Xmx']} Xms={java_memory['Xms']})"
                    )

        if found_servers:
            pInfo(f"[+] Insgesamt {len(found_servers)} Server gefunden.")
            choice = Prompt.ask(r"[deep_sky_blue2]EchoCloud[/deep_sky_blue2] > Möchtest du für alle diese Server automatisch eine Config generieren? (y/n): ").strip().lower()
            if choice == "y":
                for server in found_servers:
                    self.generate_config_for_server(server)
                pInfo("Alle Configs wurden generiert.")
            else:
                pInfo("OK, keine Configs erstellt.")

            choice = Prompt.ask(r"[deep_sky_blue2]EchoCloud[/deep_sky_blue2] > Möchtest du EchoCloud Jetzt Neustarten um alle AuthTokens Automatisch zu generieren?: ").strip().lower()
            if choice == "y":
                os.system("clear")
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                pInfo("OK.")

        else:
            pInfo("Keine Server gefunden.")

    def generate_config_for_server(self, server: 'Server'):
        cfg = {
            "server_name": server.name,
            "ip": server.ip,
            "port": server.port,
            "server_type": server.server_type,
            "java_memory": server.java_memory,
            "run_sh_path": getattr(server, "run_sh_path", None)
        }
        out_path = self.server_config_dir / f"{server.server_id}.yaml"
        with open(out_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)
        server.config_path = str(out_path)
        pInfo(f"Config erstellt: {out_path}")


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
        self.run_sh_path: str = "Unknown"
        self.state: str = "OFFLINE" # OFFLINE / ONLINE / STARTING / STOPPING

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

        if not self.run_sh_path:
            pError(f"[ERROR] Keine run.sh für Server '{self.name}' gefunden.")
            return

        try:
            # Screen-Name aus run.sh extrahieren
            with open(self.run_sh_path, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"-S\s+([^\s]+)", content)
                if match:
                    self.screen_name = match.group(1)
                else:
                    self.screen_name = f"{self.name}"

            # run.sh ausführen
            subprocess.Popen(
                ["bash", self.run_sh_path],
                cwd=str(Path(self.run_sh_path).parent),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.state = "STARTING" # Auf Antwort von API warten bis server -> ONLINE

            self.is_running = True
            self.start_time = datetime.now()
            pInfo(f"[INFO] Server '{self.name}' wurde gestartet (Screen: {self.screen_name}).")

        except Exception as e:
            pError(f"[ERROR] Konnte Server '{self.name}' nicht starten: {e}")



    def stop(self):
        self.is_running = False
        self.start_time = None
        pInfo(f"[INFO] Server '{self.name}' wurde gestoppt.")

        if not hasattr(self, "screen_name") or not self.screen_name:
            pError(f"[ERROR] Kein Screen-Name bekannt für '{self.name}', kann nicht stoppen.")
            return

        try:
            subprocess.run(
                ["screen", "-S", self.screen_name, "-p", "0", "-X", "stuff", "stop\n"],
                check=True
            )
            self.state = "STOPPING" # Auf antwort per API warten bis server -> OFFLINE
            self.is_running = False
            self.start_time = None
            pInfo(f"[INFO] Stop-Befehl an Server '{self.name}' (Screen: {self.screen_name}) gesendet.")
        except Exception as e:
            pError(f"[ERROR] Konnte Server '{self.name}' nicht stoppen: {e}")

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
            pInfo(f"{line}")
        pInfo(" ")

