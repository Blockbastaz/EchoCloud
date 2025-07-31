import yaml
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

class CLIManager:
    def __init__(self, server_config_dir="data/server_configs", settings_path="config/settings.yaml"):
        self.server_config_dir = Path(server_config_dir)
        self.server_config_dir.mkdir(parents=True, exist_ok=True)
        with open(settings_path, "r") as f:
            self.settings = yaml.safe_load(f)
        self.default_server_path = Path(self.settings["default_server_path"])

    def list_registered_servers(self):
        configs = list(self.server_config_dir.glob("*.yaml"))
        if not configs:
            console.print("[bold yellow]Keine registrierten Server gefunden.[/bold yellow]")
            return
        table = Table(title="Registrierte Server", style="cyan")
        table.add_column("Name")
        table.add_column("Typ")
        table.add_column("Dateipfad")
        for cfg_path in configs:
            with open(cfg_path, "r") as f:
                cfg = yaml.safe_load(f)
            table.add_row(cfg.get("server_name", "-"), cfg.get("server_type", "-"), str(cfg_path))
        console.print(table)

    def import_server(self):
        console.print(Panel("[bold green]Neuen Server importieren[/bold green]"))
        server_type = Prompt.ask("Server Typ (z.B. Lobby, Survival)")
        server_name = Prompt.ask("Server Name (z.B. Lobby-1)")
        xmx = Prompt.ask("Java max RAM (Xmx)", default="1024M")
        xms = Prompt.ask("Java initial RAM (Xms)", default="1024M")

        server_path = self.default_server_path / server_type / server_name
        if not server_path.exists():
            console.print(f"[red]Serverpfad {server_path} existiert nicht![/red]")
            return

        cfg = {
            "server_type": server_type,
            "server_name": server_name,
            "java_memory": {
                "Xmx": xmx,
                "Xms": xms
            }
        }
        config_path = self.server_config_dir / f"{server_name}.yaml"
        with open(config_path, "w") as f:
            yaml.dump(cfg, f)
        console.print(f"[green]Server '{server_name}' erfolgreich importiert und gespeichert unter {config_path}[/green]")

    def auto_import_servers(self):
        """
        Scannt default_server_path rekursiv und importiert alle Server,
        die es noch nicht in data/server_configs gibt.
        """
        imported = 0
        existing_names = {p.stem for p in self.server_config_dir.glob("*.yaml")}

        for server_type_dir in self.default_server_path.iterdir():
            if not server_type_dir.is_dir():
                continue
            for server_dir in server_type_dir.iterdir():
                if not server_dir.is_dir():
                    continue
                server_name = server_dir.name
                if server_name in existing_names:
                    continue

                cfg = {
                    "server_type": server_type_dir.name,
                    "server_name": server_name,
                    "java_memory": {
                        "Xmx": "1024M",
                        "Xms": "1024M"
                    }
                }
                config_path = self.server_config_dir / f"{server_name}.yaml"
                with open(config_path, "w") as f:
                    yaml.dump(cfg, f)
                imported += 1
                console.print(f"[cyan]Automatisch importiert: {server_name} ({server_type_dir.name})[/cyan]")

        if imported == 0:
            console.print("[yellow]Keine neuen Server zum automatischen Import gefunden.[/yellow]")
        else:
            console.print(f"[green]Insgesamt {imported} neue Server importiert.[/green]")

    def show_menu(self):
        while True:
            console.print("\n[bold blue]EchoCloud - Server Management[/bold blue]")
            console.print("[1] Registrierte Server anzeigen")
            console.print("[2] Server importieren (Name + Typ)")
            console.print("[3] Server automatisch importieren")
            console.print("[0] Beenden")

            choice = Prompt.ask("Bitte wählen", choices=["0", "1", "2", "3"], default="0")

            if choice == "1":
                self.list_registered_servers()
            elif choice == "2":
                self.import_server()
            elif choice == "3":
                self.auto_import_servers()
            elif choice == "0":
                console.print("[bold magenta]Auf Wiedersehen![/bold magenta]")
                break
