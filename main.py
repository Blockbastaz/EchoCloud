from core.cli import CLIManager
from core.console import showClientInfo, showBanner, pInfo
from commands.commandmanager import CommandManager
from core.server_manager import ServerManager, Server
from rich.prompt import Prompt

"""
Achtung dies ist nur ein Grobes Konzept. Es ist Keine Funktion gewährleistet.
"""

def main():
    servermanager = ServerManager()

    commandmanager = CommandManager(servermanager)

    showBanner()
    showClientInfo("1.0.2", str(len(servermanager.servers)))


    while True:
        try:
            if commandmanager.selected_server is None:
                user_input = Prompt.ask("[deep_sky_blue2]EchoCloud[/deep_sky_blue2] > ")
            else:
                user_input = Prompt.ask(f"[deep_sky_blue2]EchoCloud[/deep_sky_blue2] ([red]{commandmanager.selected_server.name}[/red]) > ")

            selected_module = commandmanager.handle_command(user_input)

        except KeyboardInterrupt:
            pInfo("\n[bold red]Beende...[/bold red]")
            break

if __name__ == "__main__":
    main()
