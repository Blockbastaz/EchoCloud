from typing import AnyStr

from rich.console import Console
from rich.prompt import Prompt
from core import debug_mode

console = Console()

def showBanner():
    try:
        with open('./data/banner.txt', 'r') as file:
            banner: AnyStr = file.read()
        console.print(banner, style="deep_sky_blue2")
    except FileNotFoundError:
        pError("banner.txt nicht gefunden in ../data/")
    except Exception as e:
        pError(f"Error reading banner: {e}")

def showClientInfo(version: str, servers: str):
    console.print(f"          + -- --=[   EchoCloud Version [yellow4]{version}  [/yellow4]]=-- -- +", style="white")
    console.print(f"          + -- --=[   [yellow4]{servers}[/yellow4] - Server Registriert   ]=-- -- +", style="white")
    print(" ")

def pInfo(text: str):
    console.print("[deep_sky_blue2][[/deep_sky_blue2][green]*[/green][deep_sky_blue2]][/deep_sky_blue2] " + text)

def pWarning(text: str):
    console.print("[deep_sky_blue2][[/deep_sky_blue2][yellow]*[/yellow][deep_sky_blue2]][/deep_sky_blue2] [yellow]" + text + "[/yellow]")

def pError(text: str):
    console.print("[deep_sky_blue2][[/deep_sky_blue2][red]*[/red][deep_sky_blue2]][/deep_sky_blue2] [red]" + text + "[/red]")


def pDebug(text: str):
    if debug_mode:
        console.print(
            "[deep_sky_blue2][[/deep_sky_blue2][purple4]*[/purple4][deep_sky_blue2]][/deep_sky_blue2] [purple4]" + text + "[/purple4]")


def pYesNoQuestion(text: str):
    """Stellt dem Benutzer eine Ja-/Nein-Frage im passenden Stil."""
    while True:
        answer = Prompt.ask(f"[blue][[/blue][cyan>?[/cyan][blue]][/blue] [cyan]{text}[/cyan] ([green]j[/green]/[red]n[/red])", choices=["j", "n"], default="n")
        if answer in ["j", "n"]:
            return answer == "j"
def clearConsole():
    console.clear()