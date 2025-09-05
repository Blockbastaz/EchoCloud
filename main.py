from rich.prompt import Prompt

from commands.commandmanager import CommandManager
from core.console import showClientInfo, showBanner, pInfo
from core.server_manager import ServerManager
from api.apimanager import APIManager
from utils.storagemanager import StorageManager
from core import (host,
                  port,
                  auth_config_path,
                  cert_file_path,
                  key_file_path,
                  auto_api,
                  storage_type,
                  storage_host,
                  storage_port,
                  storage_username,
                  storage_password,
                  storage_database,
                  storage_table_name,
                  storage_h2_file_path,
                  heartbeat_delay,
                  cert_days,
                  autocert,
                  use_https,
                  redis_channel,
                  communication_type, redis_user, redis_password)


# Pycharm importiert falsch fix -> psycopg2-binary~=2.9.10

def main():
    servermanager = ServerManager()

    storagemanager = StorageManager(storage_type,
                                    storage_host,
                                    storage_port,
                                    storage_database,
                                    storage_username,
                                    storage_password,
                                    storage_table_name,
                                    storage_h2_file_path)

    apimanager = APIManager(storage_manager=storagemanager,
                            server_manager=servermanager,
                            host=host,
                            port=port,
                            auth_config_path=auth_config_path,
                            cert_file_path=cert_file_path,
                            key_file_path=key_file_path
                            , cert_duration_days=cert_days,
                            heartbeat_delay=heartbeat_delay,
                            autocert=autocert,
                            use_https=use_https,
                            communication_type=communication_type,
                            redis_channel=redis_channel, redis_user=redis_user, redis_password=redis_password)

    if auto_api:
        apimanager.start_in_thread()

    commandmanager = CommandManager(servermanager, apimanager, storagemanager)

    showBanner()
    showClientInfo("1.0.3", str(len(servermanager.servers)))


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
