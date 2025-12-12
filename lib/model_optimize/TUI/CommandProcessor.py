from typing import Callable, Any


class CommandProcessor:
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    def __init__(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        self.commands = {}
        self.symbolics = {}
        self.symbolic_groups = {}
        self.actions_after_symbolic = []
        self.register_command("exit", lambda *args: None, helpmsg="Shutdown the application")
        self.register_command("help", self.print_help, helpmsg="Show the help menu")
        
    def register_command(self, name: str, func: Callable, args: list = [], helpmsg: str = ""):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        self.commands[name] = {
            "func": func,
            "args": args,
            "helpmsg": helpmsg
        }
    
    def register_symbolic_group(self, group: str, group_name: str):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if not group in self.symbolics:
            self.symbolics[group] = {"specs":{}, "props":{}}
        self.symbolic_groups[group] = group_name
        return group

    def register_symbolic_spec(self, spec: str, group: str, get_obj: Callable[[], object], helpmsg: str = None):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if not group in self.symbolics:
            raise KeyError(f"Group {group} does not exist")
        self.symbolics[group]["specs"][spec] = {
            "obj": get_obj,
            "helpmsg": helpmsg
        }
        
    def register_symbolic_prop(self, prop: str, group: str, getter: Callable[[object], Any], setter: Callable[[object, object], bool], dtype: type, helpmsg: str = None):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if not group in self.symbolics:
            raise KeyError(f"Group {group} does not exist")
        self.symbolics[group]["props"][prop] = {
            "getter": getter,
            "setter": setter,
            "dtype": dtype,
            "helpmsg": helpmsg
        }
        
    def register_action_after_symbolic(self, fn: Callable[[], None]):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        self.actions_after_symbolic.append(fn)
        
    def get_symbolic_group(self, spec: str):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        specs = {
            spec:group 
            for group, data in self.symbolics.items() 
            for spec in data["specs"]
        }
        if spec in specs:
            return specs[spec]
        return False
        
    def process_command(self, cmd: str):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        tokens = cmd.split(" ")
        
        if not tokens:
            return
        
        if self.process_literal(tokens):
            return
        
        if self.process_symbolic(tokens):
            self.execute_after_symbolic()
            return
        
        print("Unknown command, type 'help'")
        
    def process_symbolic(self, tokens: list):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        token_length = len(tokens)
        if token_length != 2 and token_length != 3:
            return False
        
        spec = tokens[0]
        prop = tokens[1]
        
        group = self.get_symbolic_group(spec)
        
        if not group or not prop in self.symbolics[group]["props"]:
            return False

        spec_d = self.symbolics[group]["specs"][spec]
        prop_d = self.symbolics[group]["props"][prop]
        obj = spec_d["obj"]()

        if token_length == 2:
            val = prop_d["getter"](obj)
            print(f"{spec}.{prop} = {val}")
        else:
            val = tokens[2]
            dtype = prop_d["dtype"]
            try:
                val = dtype(val)
            except (ValueError, TypeError):
                print(f"ERROR: Cannot cast, {spec}.{prop} is an {dtype.__name__} (entered value: {val})")
            else:
                prop_d["setter"](obj, val)
        
        return True
        
        
    def process_literal(self, tokens: list):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        name = tokens[0]
        if name not in self.commands:
            return False
        
        cmd = self.commands[name]
        argc = len(cmd["args"])
        given = tokens[1:]

        if len(given) != argc:
            self.print_arg_error(name)
            return True

        # call with unpacked args
        cmd["func"](*given)
        return True
    
    def execute_after_symbolic(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        for fn in self.actions_after_symbolic:
            fn()
    
    def print_arg_error(self, name: str):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        cmd = self.commands[name]
        args = " ".join(f"<{a}>" for a in cmd["args"])
        print(f"Usage: {name} {args}")
        
    def print_help(self, *_):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        print("\nCommands:")
        
        for name, meta in sorted(self.commands.items()):
            args = " ".join(f"<{a}>" for a in meta["args"])
            print(f"  {name:10} {args:20} {meta['helpmsg']}")
        
        print("\nSymbolic groups:")
        for name, helpmsg in sorted(self.symbolic_groups.items()):
            print(f"  {name:15} {helpmsg}")
            
        print("\nSymbolic parameters:")
        print('  Usage:')
        print("    <specifier> <prop> <value> to set specifier.prop to value")
        print("    <specifier> <prop>         to print specifier.prop\n")
        for group in self.symbolics:
            print(f"  {group}")
            print("    Specifiers:")
            for spec, meta in sorted(self.symbolics[group]["specs"].items()):
                print(f"      {spec:10} {meta["helpmsg"]}")
            print("    Props:")
            for spec, meta in sorted(self.symbolics[group]["props"].items()):
                print(f"      {spec:10} {f'<{meta["dtype"].__name__}>':8} {meta["helpmsg"]}")
                
    def get_autocompletion_dict(self):
        # Add the commands 
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        autocompletion = {command:None for command in self.commands}
            
        # Add the symbolics
        for group in self.symbolics:
            specs = self.symbolics[group]["specs"]
            props = self.symbolics[group]["props"]
            for spec in specs:
                autocompletion[spec] = {}
                for prop in props:
                    autocompletion[spec][prop] = None
        
        return autocompletion