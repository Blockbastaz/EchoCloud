import locale
import sys

from api.apimanager import APIManager
from commands.commandcompleter import setup_readline, safe_input_with_readline
from commands.commandmanager import CommandManager
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
from core.console import showClientInfo, showBanner, pInfo, register_reset_at_shutdown
from core.server_manager import ServerManager
from utils.storagemanager import StorageManager

# Terminal Reset beim beenden
register_reset_at_shutdown()


# Pycharm importiert falsch fix -> psycopg2-binary~=2.9.10

def main():
    # UTF-8 erzwingen
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr.reconfigure(encoding='utf-8')

    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except locale.Error:
            pass

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
                            key_file_path=key_file_path,
                            cert_duration_days=cert_days,
                            heartbeat_delay=heartbeat_delay,
                            autocert=autocert,
                            use_https=use_https,
                            communication_type=communication_type,
                            redis_channel=redis_channel,
                            redis_user=redis_user,
                            redis_password=redis_password)

    if auto_api:
        apimanager.start_in_thread()

    commandmanager = CommandManager(servermanager, apimanager, storagemanager)
    setup_readline(commandmanager)

    showBanner()
    showClientInfo("1.0.3", str(len(servermanager.servers)))

    while True:
        try:
            # Prompt als Klartext ausgeben, nicht mit rich
            if commandmanager.selected_server is None:
                sys.stdout.write("EchoCloud > ")
            else:
                sys.stdout.write(f"EchoCloud ({commandmanager.selected_server.name}) > ")
            sys.stdout.flush()

            # Eingabe lesen (mit readline)
            user_input = safe_input_with_readline("")
            commandmanager.handle_command(user_input)

        except KeyboardInterrupt:
            pInfo("\n[bold red]Beende...[/bold red]")
            break
        except EOFError:
            pInfo("\n[bold red]Beende...[/bold red]")
            break


if __name__ == "__main__":
    main()