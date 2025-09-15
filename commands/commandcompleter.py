import os

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings


class EchoCloudCompleter(Completer):
    """Tab completion handler for EchoCloud commands using prompt_toolkit"""

    def __init__(self, command_manager):
        self.command_manager = command_manager

    def get_completions(self, document, complete_event):
        """Generate completions based on current input"""
        text = document.text
        parts = text.split()
        word_before_cursor = document.get_word_before_cursor()

        if not parts or (len(parts) == 1 and not text.endswith(' ')):
            # Complete command names
            commands = list(self.command_manager.commands.keys())
            for cmd in commands:
                if cmd.startswith(word_before_cursor):
                    yield Completion(cmd, start_position=-len(word_before_cursor))

        elif len(parts) >= 1:
            # Complete based on first command
            cmd = parts[0].lower()
            if cmd == 'select' and len(parts) <= 2:
                # Complete server names for 'select' command
                if hasattr(self.command_manager, 'server_manager') and self.command_manager.server_manager.servers:
                    server_ids = [server.server_id for server in self.command_manager.server_manager.servers]
                    server_names = [server.name for server in self.command_manager.server_manager.servers]
                    all_servers = server_ids + server_names
                    for server in all_servers:
                        if server.startswith(word_before_cursor):
                            yield Completion(server, start_position=-len(word_before_cursor))

            elif cmd == 'execute' and len(parts) <= 2:
                # Complete minecraft commands for 'execute' command
                common_commands = [
                    "say", "stop", "reload", "whitelist", "op", "deop", "kick", "ban",
                    "pardon", "gamemode", "tp", "give", "time", "weather", "difficulty",
                    "gamerule", "seed", "list", "save-all", "save-off", "save-on"
                ]
                for cmd_name in common_commands:
                    if cmd_name.startswith(word_before_cursor):
                        yield Completion(cmd_name, start_position=-len(word_before_cursor))


def create_key_bindings():
    """Create custom key bindings to match readline behavior"""
    kb = KeyBindings()

    # History search like readline (Arrow up/down with prefix search)
    @kb.add('up')
    def _(event):
        event.app.current_buffer.history_backward(count=event.arg)

    @kb.add('down')
    def _(event):
        event.app.current_buffer.history_forward(count=event.arg)

    return kb


class EchoCloudPrompt:
    """Enhanced prompt handler using prompt_toolkit"""

    def __init__(self, command_manager):
        self.command_manager = command_manager

        # Setup history file
        self.history_file = os.path.expanduser('~/.echocloud_history')

        # Create completer
        self.completer = EchoCloudCompleter(command_manager)

        # Create key bindings
        self.key_bindings = create_key_bindings()

        # Create session with all configurations
        self.session = PromptSession(
            history=FileHistory(self.history_file),
            completer=self.completer,
            key_bindings=self.key_bindings,
            # Completion settings to match readline behavior
            complete_while_typing=False,  # Only complete on TAB
        )

    def get_prompt_text(self):
        """Generate the prompt text based on current state"""
        if self.command_manager.selected_server is None:
            return "EchoCloud > "
        else:
            return f"EchoCloud ({self.command_manager.selected_server.name}) > "

    def get_input(self):
        """Get input with proper prompt and completion"""
        try:
            prompt_text = self.get_prompt_text()
            user_input = self.session.prompt(prompt_text)
            return user_input
        except UnicodeDecodeError:
            try:
                return self.session.prompt(prompt_text).encode('latin-1').decode('utf-8')
            except (UnicodeDecodeError, UnicodeEncodeError):
                return self.session.prompt(prompt_text).encode('utf-8', errors='ignore').decode('utf-8')
        except EOFError:
            raise KeyboardInterrupt


def setup_prompt_toolkit(command_manager):
    """Setup prompt_toolkit with command manager"""
    return EchoCloudPrompt(command_manager)


# Backward compatibility function
def safe_input_with_readline():
    """Backward compatibility - this shouldn't be used with prompt_toolkit"""
    try:
        return input()
    except UnicodeDecodeError:
        try:
            return input().encode('latin-1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return input().encode('utf-8', errors='ignore').decode('utf-8')
    except EOFError:
        raise KeyboardInterrupt


# For backward compatibility - but prompt_toolkit handles this better
def setup_readline(command_manager):
    """Backward compatibility function - use setup_prompt_toolkit instead"""
    pass


# Example usage for main loop
def main_loop_example(command_manager):
    """Example usage in main loop with prompt_toolkit"""
    echo_prompt = setup_prompt_toolkit(command_manager)

    while True:
        try:
            user_input = echo_prompt.get_input()
            if user_input.strip():
                # Process the command
                print(f"Verarbeite: {user_input}")
        except KeyboardInterrupt:
            print("\nAuf Wiedersehen!")
            break
        except Exception as e:
            print(f"Fehler: {e}")
            continue