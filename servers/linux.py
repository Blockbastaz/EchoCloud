import subprocess
import os


class LinuxServer:
    def __init__(self, config: dict):
        self.name = config["name"]
        self.path = config["path"]
        self.java_args = config["java_args"]
        self.screen_name = config["screen_name"]

    def start(self):
        if not os.path.exists(self.path):
            return {"error": f"Server path does not exist: {self.path}"}

        command = f"cd {self.path} && screen -dmS {self.screen_name} {self.java_args}"
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            return {"status": "started", "server": self.name}
        else:
            return {"error": f"Failed to start server: {self.name}"}

    def stop(self):
        command = f"screen -S {self.screen_name} -X quit"
        result = subprocess.run(command, shell=True)
        if result.returncode == 0:
            return {"status": "stopped", "server": self.name}
        else:
            return {"error": f"Failed to stop server: {self.name}"}
