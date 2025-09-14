import os
import sys
from typing import Dict, Callable, Optional, TYPE_CHECKING, List, Tuple

from rich.prompt import Prompt

import core
import core.console as utils
from core.server_manager import ServerManager
from api.apimanager import APIManager
from utils.storagemanager import StorageManager

if TYPE_CHECKING:
    from core.server_manager import Server


class CommandManager:
    def __init__(self, server_manager: 'ServerManager', api_manager: APIManager, storage_manager: StorageManager):
        self.server_manager: ServerManager = server_manager
        self.api_manager = api_manager
        self.selected_server: Optional[Server] = None  # Module = Server Plugin
        self.commands: Dict[str, Callable[[str], None]] = {}
        self.command_infos: List[Tuple[str, str]] = []
        self.storage_manager = storage_manager

        # Commands registrieren
        self.register_command("status", self.cmd_status)
        self.register_command("servers", self.cmd_servers)
        self.register_command("select", self.cmd_select)
        self.register_command("config", self.cmd_config)
        self.register_command("start", self.cmd_start)
        self.register_command("stop", self.cmd_stop)
        self.register_command("logs", self.cmd_logs)
        self.register_command("help", self.cmd_help)
        self.register_command("autoscan", self.cmd_autoscan)
        self.register_command("debug", self.cmd_debug)
        self.register_command("reload", self.cmd_reload)
        self.register_command("startapi", self.cmd_startapi)
        self.register_command("execute", self.cmd_execute)
        self.register_command("exit", self.cmd_exit)

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
        self.add_help_message("autoscan", "Scannt nach neuen Servern")
        self.add_help_message("help", "Diese Hilfe anzeigen")
        self.add_help_message("startapi", "Startet den API Webserver")
        self.add_help_message("execute <command>", "Führt einen Befehl auf einem Server aus")
        self.add_help_message("exit", "Stoppt EchoCloud")

    def add_help_message(self, command: str, info: str):
        self.command_infos.append((command, info))

    def register_command(self, name, func):
        self.commands[name] = func

    def get_command_completions(self, text: str) -> List[str]:
        """Get list of commands that start with the given text"""
        return [cmd for cmd in self.commands.keys() if cmd.startswith(text.lower())]

    def get_server_completions(self, text: str) -> List[str]:
        """Get list of server IDs and names that start with the given text"""
        if not self.server_manager.servers:
            return []

        completions = []
        for server in self.server_manager.servers:
            if server.server_id.startswith(text):
                completions.append(server.server_id)
            if server.name.startswith(text):
                completions.append(server.name)

        return completions

    def get_completions_for_command(self, command: str, args: str) -> List[str]:
        """Get completions based on command context"""
        command = command.lower()

        if command == "select":
            return self.get_server_completions(args)
        elif command == "config" and self.selected_server:
            # Add config key completions if server is selected
            if hasattr(self.selected_server, 'java_memory'):
                return [key for key in self.selected_server.java_memory.keys() if key.startswith(args)]
        elif command == "execute" and self.selected_server:
            # Common Minecraft server commands for tab completion
            common_commands = [
                "say", "stop", "reload", "whitelist", "op", "deop", "kick", "ban",
                "pardon", "gamemode", "tp", "give", "time", "weather", "difficulty",
                "gamerule", "seed", "list", "save-all", "save-off", "save-on"
            ]
            return [cmd for cmd in common_commands if cmd.startswith(args)]

        return []

    def handle_command(self, entered: str):
        entered = entered.strip()
        if not entered:
            return
        parts = entered.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            utils.pWarning("Unbekannter Befehl. Tippe 'help' für eine Liste.")

    def cmd_status(self, args):
        """Zeigt Status des ausgewählten Servers an"""
        if self.selected_server:
            self.selected_server.display_status()  # Beispielmethode
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
            utils.pWarning("Bitte Server-ID oder Namen angeben: select <server_id|server_name>")
            if self.server_manager.servers:
                utils.pInfo("Verfügbare Server:")
                for server in self.server_manager.servers:
                    utils.pInfo(f" - {server.server_id}: {server.name}")
            return

        # Try to find server by ID first, then by name
        server = self.server_manager.get_server_by_id(args)
        if not server:
            # Try to find by name
            for s in self.server_manager.servers:
                if s.name.lower() == args.lower():
                    server = s
                    break

        if server:
            self.selected_server = server
            utils.pInfo(f"Server [cyan]{server.name}[/cyan] wurde ausgewählt.")
        else:
            utils.pWarning(f"Server mit ID/Namen '{args}' wurde nicht gefunden.")

    # TEST
    def cmd_config(self, args):
        """Zeigt oder setzt Konfiguration des Servers"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if not args:
            # Show all config
            utils.pInfo("Server-Konfiguration:")
            if hasattr(self.selected_server, 'java_memory'):
                for key, value in self.selected_server.java_memory.items():
                    utils.pInfo(f"  {key}: {value}")
        else:
            # Handle config get/set
            config_parts = args.split(" ", 1)
            key = config_parts[0]

            if len(config_parts) == 1:
                # Get specific config value
                if hasattr(self.selected_server, 'java_memory') and key in self.selected_server.java_memory:
                    utils.pInfo(f"{key}: {self.selected_server.java_memory[key]}")
                else:
                    utils.pWarning(f"Konfigurationskey '{key}' nicht gefunden.")
            else:
                # Set config value
                value = config_parts[1]
                utils.pInfo(f"TODO: Setze {key} = {value}")

    # TEST
    def cmd_start(self, args):
        """Startet den ausgewählten Server"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if self.selected_server.is_running:
            utils.pWarning("Server läuft bereits.")
            return

        self.selected_server.start()

    def cmd_execute(self, args):
        """Führt einen Befehl auf dem Server aus"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if not self.selected_server.is_running:
            utils.pWarning("Server ist nicht online.")
            return

        if not args:
            utils.pWarning("Bitte Befehl angeben: execute <command>")
            return

        utils.pInfo(f"Führe Befehl aus: {args}")
        self.selected_server.send_command(args)

    # TEST
    def cmd_stop(self, args):
        """Stoppt den ausgewählten Server"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if not self.selected_server.is_running:
            utils.pWarning("Server ist bereits gestoppt.")
            return

        self.selected_server.stop()

    # TEST
    def cmd_logs(self, args):
        """Zeigt letzte Log-Zeilen des Servers"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        if not self.selected_server.last_output_lines:
            utils.pInfo("Keine Logs verfügbar.")
            return

        utils.pInfo("Server Logs:")
        for line in self.selected_server.last_output_lines[-20:]:  # Show last 20 lines
            utils.pInfo(line)

    # TODO server reloaden via /reload
    def cmd_reload(self, args):
        """Lädt Server-Konfiguration neu"""
        if not self.selected_server:
            utils.pWarning("Kein Server ausgewählt.")
            return

        utils.pInfo(f"TODO: Reload {self.selected_server.name}")

    def cmd_debug(self, args):
        """Aktiviert/Deaktiviert Entwickler Modus"""
        tmp = not core.debug_mode
        core.debug_mode = not core.debug_mode

        if tmp:
            utils.pInfo("Debug Mode aktiviert")
        else:
            utils.pInfo("Debug Mode deaktiviert")

    def cmd_help(self, args):
        """Zeigt Hilfe"""
        utils.pInfo("Verfügbare Befehle:")
        for cmd, description in self.command_infos:
            utils.pInfo(f" - {cmd:<18} -> {description}")

        utils.pInfo("\nTipps:")
        utils.pInfo(" - Nutze TAB für Auto-Completion")
        utils.pInfo(" - Nutze Pfeiltasten ↑/↓ für Command History")

    def cmd_autoscan(self, args):
        """Importiert automatisch neue Server"""
        self.server_manager.scan_servers()
        utils.pInfo(f"Server Erfolgreich gescannt.")

    def cmd_startapi(self, args):
        """Startet den API Webserver"""
        self.api_manager.start_in_thread()
        utils.pInfo(f"API Webserver gestartet.")

    def cmd_exit(self, args):
        """Beendet EchoCloud"""
        self.api_manager.stop_thread()
        self.storage_manager.close()
        utils.pInfo(f"[red]Bye Bye...[/red]")
        sys.exit(-1)