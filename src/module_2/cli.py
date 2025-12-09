from lib.model.generate import *
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import NestedCompleter
import threading
import queue
from time import sleep

class CLI:
    def __init__(self, cmd_queue: "queue.Queue[str]", stop_event: threading.Event, executing_event: threading.Event, cancelled_event: threading.Event,
                 autocompletion_dict: dict|None = None):
        self.cmd_queue = cmd_queue
        self.stop_event = stop_event
        self.executing_event = executing_event
        self.cancelled_event = cancelled_event
        self.t = None
        self.set_autocompletion_dict(autocompletion_dict or {})
    
    def cli(self):
        session = PromptSession(history=InMemoryHistory())
        print("CLI thread started. Type 'help' for commands. Use arrow keys for history.")
        
        while not self.stop_event.is_set():
            try:
                while self.executing_event.is_set() and not self.stop_event.is_set():
                    sleep(0.05)
                    
                self.cancelled_event.clear()
                    
                user_input = session.prompt("> ", completer=self.completer).strip()
                
                if not user_input:
                    continue
                
                self.cmd_queue.put(user_input)
                self.executing_event.set()
                
                if user_input == "exit":
                    self.exit(put_cmd=False)
                    return
            except KeyboardInterrupt: # Ctrl+C pressed
                self.cancelled_event.set()
                continue
            except EOFError: # Ctrl+D pressed
                self.exit()
                return
            except Exception as e:
                # log and continue
                print("CLI error:", e)
                self.exit()
                return
            
    def set_autocompletion_dict(self, autocompletion_dict: dict):
        self.completer = NestedCompleter.from_nested_dict(autocompletion_dict)
            
    def exit(self, put_cmd=True):
        self.stop_event.set()
        self.cmd_queue.put("exit")
        return
    def run(self):
        self.t = threading.Thread(target=self.cli, daemon=True)
        self.t.start()
    def close(self):
        self.exit(put_cmd=False)
        self.t.join(timeout=1.0)