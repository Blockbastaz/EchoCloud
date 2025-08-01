from typing import Dict, Callable, Optional, TYPE_CHECKING, List, Tuple

from rich.prompt import Prompt

import core
import core.console as utils
from core.console import pInfo
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

    def cmd_servers(self, args):
        """Listet alle verfügbaren Server auf"""
        utils.pInfo(f"Verfügbare Server: {len(self.modules)}")
        for srv in self.server_manager.servers:
            utils.pInfo(f"TODO")
            #TODO

    def cmd_select(self, args):
        """Wählt einen Server zum Verwalten aus"""
        if not args:
            utils.pWarning("Bitte Server-ID angeben: select <server_id>")
            return
        if args in self.modules:
            self.selected_server = self.modules[args]
            utils.pInfo(f"Server [cyan]{args}[/cyan] ausgewählt.")
        else:
            utils.pWarning("Server nicht gefunden.")

    def cmd_config(self, args):
        """Zeigt oder setzt Konfigurationen am Server"""
        pInfo("TODO!")
        #TODO

    def cmd_start(self, args):
        """Startet den ausgewählten Server"""
        pInfo("TODO!")
        #TODO

    def cmd_stop(self, args):
        """Stoppt den ausgewählten Server"""
        pInfo("TODO!")
        #TODO

    def cmd_logs(self, args):
        """Zeigt Logs des ausgewählten Servers"""
        pInfo("TODO!")
        #TODO

    def cmd_reload(self, args):
        utils.pInfo("TODO!")
        #TODO

    def cmd_debug(self, args):
        core.debugMode = not core.debugMode
        if core.debugMode:
            utils.pDebug("Debug Mode aktiviert")
        else:
            utils.pInfo("Debug Mode deaktiviert")

    def cmd_help(self, args):
        utils.pInfo("Verfügbare Befehle:")
        for cmd, description in self.command_infos:
            utils.pInfo(f" - {cmd:<18} -> {description}")

