import os
import subprocess
from pathlib import Path

class LinuxServerManager:
    def __init__(self, config: dict, base_path: str, server_version: str):
        self.config = config
        self.base_path = Path(base_path)
        self.server_version = server_version

    def get_server_path(self):
        # Beispiel: ../Cloud/running/static/Lobby/Lobby-1
        return self.base_path / self.config['server_type'] / self.config['server_name']

    def get_screen_name(self):

        return self.config['server_name']

    def is_screen_running(self):
        screen_name = self.get_screen_name()
        try:
            output = subprocess.check_output(['screen', '-ls'], text=True)
            return screen_name in output
        except subprocess.CalledProcessError:
            return False

    def start_server(self):
        if self.is_screen_running():
            print(f"Server {self.get_screen_name()} läuft bereits.")
            return False

        server_path = self.get_server_path()
        run_sh = server_path / "run.sh"

        if not run_sh.exists():
            self._create_run_sh(server_path)

        subprocess.run(['chmod', '+x', str(run_sh)])
        subprocess.run([str(run_sh)])

        print(f"Server {self.get_screen_name()} gestartet.")
        return True

    def stop_server(self):
        if not self.is_screen_running():
            print(f"Server {self.get_screen_name()} läuft nicht.")
            return False

        screen_name = self.get_screen_name()
        # Sendet "stop" an den Screen
        subprocess.run(['screen', '-S', screen_name, '-p', '0', '-X', 'stuff', 'stop\n'])

        print(f"Stop-Befehl an Server {screen_name} gesendet.")
        return True

    def _create_run_sh(self, server_path: Path):
        java_mem = self.config.get('java_memory', {})
        xmx = java_mem.get('Xmx', '1024M')
        xms = java_mem.get('Xms', '1024M')

        jar_file = self.server_version
        run_sh_content = f"""#!/bin/bash
screen -dmS {self.get_screen_name()} java -Xmx{xmx} -Xms{xms} -jar ./{jar_file}
"""

        with open(server_path / "run.sh", "w") as f:
            f.write(run_sh_content)
        print(f"run.sh für Server {self.get_screen_name()} erstellt.")
