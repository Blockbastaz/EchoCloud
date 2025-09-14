import atexit
import os
import readline


class EchoCloudCompleter:
    """Tab completion handler for EchoCloud commands"""

    def __init__(self, command_manager):
        self.command_manager = command_manager

    def complete(self, text, state):
        """Complete function for readline"""
        if state == 0:
            # First call - generate matches
            self.matches = []
            line = readline.get_line_buffer()
            parts = line.split()

            if not parts or (len(parts) == 1 and not line.endswith(' ')):
                # Complete command names
                commands = list(self.command_manager.commands.keys())
                self.matches = [cmd for cmd in commands if cmd.startswith(text)]
            elif len(parts) >= 1:
                # Complete based on first command
                cmd = parts[0].lower()
                if cmd == 'select' and len(parts) <= 2:
                    # Complete server names for 'select' command
                    if hasattr(self.command_manager, 'server_manager') and self.command_manager.server_manager.servers:
                        server_ids = [server.server_id for server in self.command_manager.server_manager.servers]
                        server_names = [server.name for server in self.command_manager.server_manager.servers]
                        all_servers = server_ids + server_names
                        self.matches = [server for server in all_servers if server.startswith(text)]
                elif cmd == 'execute' and len(parts) <= 2:
                    # Complete minecraft commands for 'execute' command
                    common_commands = [
                        "say", "stop", "reload", "whitelist", "op", "deop", "kick", "ban",
                        "pardon", "gamemode", "tp", "give", "time", "weather", "difficulty",
                        "gamerule", "seed", "list", "save-all", "save-off", "save-on"
                    ]
                    self.matches = [cmd for cmd in common_commands if cmd.startswith(text)]

        # Return next match
        try:
            return self.matches[state]
        except IndexError:
            return None


def setup_readline(command_manager):
    """Setup readline with history and tab completion"""

    # History file path
    history_file = os.path.expanduser('~/.echocloud_history')

    # Load history if it exists
    try:
        readline.read_history_file(history_file)
        # Limit history size
        readline.set_history_length(1000)
    except FileNotFoundError:
        pass

    # Save history on exit
    atexit.register(readline.write_history_file, history_file)

    # Setup tab completion
    completer = EchoCloudCompleter(command_manager)
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')

    # Enable history search with arrow keys
    readline.parse_and_bind('"\e[A": history-search-backward')
    readline.parse_and_bind('"\e[B": history-search-forward')

    # Additional readline settings for better experience
    readline.parse_and_bind('set completion-ignore-case on')
    readline.parse_and_bind('set show-all-if-ambiguous on')
    readline.parse_and_bind('set completion-map-case on')


def safe_input_with_readline(prompt_text):
    """Safe input function using readline with fallback"""
    try:
        # Use readline for input (supports history and tab completion)
        return input(prompt_text)
    except UnicodeDecodeError:
        # Fallback for encoding issues
        try:
            return input(prompt_text).encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return input(prompt_text).encode('utf-8', errors='ignore').decode('utf-8')
    except EOFError:
        # Handle Ctrl+D
        raise KeyboardInterrupt