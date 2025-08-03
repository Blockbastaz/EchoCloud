from rich.prompt import Prompt

from commands.commandmanager import CommandManager
from core.console import showClientInfo, showBanner, pInfo
from core.server_manager import ServerManager
from api.apimanager import APIManager
from core import host, port, auth_config_path, cert_file_path, key_file_path

"""
Achtung dies ist nur ein Grobes Konzept. Es ist Keine Funktion gewährleistet.
"""

def main():
    servermanager = ServerManager()

    commandmanager = CommandManager(servermanager)

    apimanager = APIManager(server_manager=servermanager, host=host, port=port, auth_config_path=auth_config_path, cert_file_path=cert_file_path, key_file_path=key_file_path)

    apimanager.start_in_thread()

    showBanner()
    showClientInfo("1.0.2", str(len(servermanager.servers)))


    while True:
        try:
            if commandmanager.selected_server is None:
                user_input = Prompt.ask("[deep_sky_blue2]EchoCloud[/deep_sky_blue2] > ")
            else:
                user_input = Prompt.ask(f"[deep_sky_blue2]EchoCloud[/deep_sky_blue2] ([red]{commandmanager.selected_server.name}[/red]) > ")

            commandmanager.handle_command(user_input)

        except KeyboardInterrupt:
            pInfo("\n[bold red]Beende...[/bold red]")
            break

if __name__ == "__main__":
    main()
