from rich.prompt import Prompt

from commands.commandmanager import CommandManager
from core.console import showClientInfo, showBanner, pInfo
from core.server_manager import ServerManager
from api.apimanager import APIManager
from core import host, port, auth_config_path, cert_file_path, key_file_path, auto_api

"""
Achtung dies ist nur ein Grobes Konzept. Es ist Keine Funktion gewährleistet.
"""

def main():
    servermanager = ServerManager()

    apimanager = APIManager(server_manager=servermanager, host=host, port=port, auth_config_path=auth_config_path, cert_file_path=cert_file_path, key_file_path=key_file_path)
    if auto_api: # API Webserver Automatisch starten
        apimanager.start_in_thread()

    commandmanager = CommandManager(servermanager, apimanager)

    showBanner()
    showClientInfo("1.0.2", str(len(servermanager.servers)))


    while True:
        try:
            if commandmanager.selected_server is None:
                user_input = Prompt.ask(r"[deep_sky_blue2]EchoCloud[/deep_sky_blue2] > ")
            else:
                user_input = Prompt.ask(f"[deep_sky_blue2]EchoCloud[/deep_sky_blue2] ([red]{commandmanager.selected_server.name}[/red]) > ")

            commandmanager.handle_command(user_input)

        except KeyboardInterrupt:
            pInfo("\n[bold red]Beende...[/bold red]")
            break

if __name__ == "__main__":
    main()
