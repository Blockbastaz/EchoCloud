from typing import Dict, Callable, Optional, TYPE_CHECKING, List, Tuple

from rich.prompt import Prompt

import core
import core.console as utils
from core.server_manager import ServerManager

if TYPE_CHECKING:
    from core.server_manager import Server

class CommandManager:
    def __init__(self, server_manager: 'ServerManager'):
        self.server_manager: ServerManager = server_manager
        self.selected_server: Optional[Server] = None  # Module = Server Plugin
        self.commands: Dict[str, Callable[[str], None]] = {}
        self.command_infos: List[Tuple[str, str]] = []

        # Commands registrieren
        self.register_command("status", self.cmd_status)
        self.register_command("servers", self.cmd_servers)
        self.register_command("select", self.cmd_select)
        self.register_command("config", self.cmd_config)
        self.register_command("start", self.cmd_start)
        self.register_command("stop", self.cmd_stop)
        self.register_command("logs", self.cmd_logs)
        self.register_command("help", self.cmd_help)
        self.register_command("debug", self.cmd_debug)
        self.register_command("reload", self.cmd_reload)

        self.add_default_commands()

    def add_default_commands(self):
        self.add_help_message("servers", "Listet alle Server")
        self.add_help_message("select <server>", "Wählt Server aus")
        self.add_help_message("status", "Zeigt Status des Servers")
        self.add_help_message("config [opt val]", "Zeigt oder setzt Server-Konfiguration")
        self.add_help_message("start", "Startet den Server")
        self.add_help_message("stop", "Stoppt den Server")
        self.add_help_message("reload", "Lädt einen Server neu")
        self.add_help_message("logs", "Zeigt Server-Logs")
        self.add_help_message("debug", "Debug Modus an/aus")
        self.add_help_message("help", "Diese Hilfe anzeigen")

    def add_help_message(self, command: str,  info: str):
        self.command_infos.append((command, info))

    def register_command(self, name, func):
        self.commands[name] = func

    def get_prompt(self):
        if self.selected_server is None:
            return Prompt.ask("[blue]echocloud[/blue] > ")
        else:
            return Prompt.ask(f"[blue]echocloud[/blue] ([cyan]{self.selected_server.module_id}[/cyan]) > ")

    def handle_command(self, entered: str):
        entered = entered.strip()
        if not entered:
            return
        parts = entered.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            self.commands[cmd](args)
        elif self.selected_server and cmd in self.selected_server.methods:
            self.call_server_method(cmd, args)
        else:
            utils.pWarning("Unbekannter Befehl. Tippe 'help' für eine Liste.")


    # Commands

    def cmd_status(self, args):
        """Zeigt Status des ausgewählten Servers an"""
        if self.selected_server:
            status = self.selected_server.get_status()  # Beispielmethode
            utils.pInfo(f"Status von [cyan]{self.selected_server.module_id}[/cyan]: \n{status}")
        else:
            utils.pWarning("Kein Server ausgewählt. Nutze 'servers' um Server anzuzeigen.")

    # TEST
    def cmd_servers(self, args):
        """Listet alle verfügbaren Server auf"""
        if not self.server_manager.servers:
            utils.pInfo("Keine Server gefunden.")
            return

        utils.pInfo("Verfügbare Server:")
        for server in self.server_manager.servers:
            status = "[green]🟢 Online[/green]" if server.is_running else "[red]🔴 Offline[/red]"
            utils.pInfo(f" - [cyan]{server.server_id}[/cyan]: {server.name} ({status})")
    # TEST
    def cmd_select(self, args):
        """Wählt einen Server zum Verwalten aus"""
        if not args:
            utils.pWarning("Bitte Server-ID angeben: select <server_id>")
            return

        server = self.server_manager.get_server_by_id(args)
        if server:
            self.selected_server = server
            utils.pInfo(f"Server [cyan]{server.name}[/cyan] wurde ausgewählt.")
        else:
            utils.pWarning(f"Server mit ID '{args}' wurde nicht gefunden.")

    # TEST
    def cmd_config(self, args):
        """Zeigt Konfiguration des Servers"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        #TODO Gesamte Konfiguration des Server anzeigen!
        utils.pInfo("Server-Konfiguration:")
        for key, value in self.selected_server.java_memory.items():
            utils.pInfo(f"  {key}: {value}")

    # TEST
    def cmd_start(self, args):
        """Startet den ausgewählten Server"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if self.selected_server.is_running:
            utils.pWarning("Server läuft bereits.")
            return

        result = self.server_manager.start_server(self.selected_server.config_path)
        if result:
            self.selected_server.start()
        else:
            utils.pError("Start fehlgeschlagen.")

    # TEST
    def cmd_stop(self, args):
        """Stoppt den ausgewählten Server"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if not self.selected_server.is_running:
            utils.pWarning("Server ist bereits gestoppt.")
            return

        result = self.server_manager.stop_server(self.selected_server.config_path)
        if result:
            self.selected_server.stop()
        else:
            utils.pError("Stop fehlgeschlagen.")

    # TEST
    def cmd_logs(self, args):
        """Zeigt letzte Log-Zeilen des Servers"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if not self.selected_server.last_output_lines:
            utils.pInfo("Keine Logs verfügbar.")
            return

    #TODO server reloaden via /reload
    def cmd_reload(self, args):
        """Lädt Server-Konfiguration neu"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        utils.pInfo(f"TODO!")

    def cmd_debug(self, args):
        tmp = not core.debug_mode
        core.debug_mode = not core.debug_mode

        if tmp:
            utils.pInfo("Debug Mode aktiviert")
        else:
            utils.pInfo("Debug Mode deaktiviert")

    def cmd_help(self, args):
        utils.pInfo("Verfügbare Befehle:")
        for cmd, description in self.command_infos:
            utils.pInfo(f" - {cmd:<18} -> {description}")

