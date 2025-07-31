from core.cli import CLIManager
from utils.logger import setup_logger

"""
Achtung dies ist nur ein Grobes Konzept. Es ist Keine Funktion gewährleistet.
"""

def main():
    setup_logger()
    cli = CLIManager()
    cli.show_menu()

if __name__ == "__main__":
    main()
