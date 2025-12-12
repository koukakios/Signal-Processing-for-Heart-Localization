from lib.model_optimize.GUI.Plot import Plot
from lib.model_optimize.GUI.CommandProcessor import CommandProcessor

def generateStandardCommands(plot: Plot) -> CommandProcessor:
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    cp = CommandProcessor()
    
    cp.register_command("reset", plot.reset, helpmsg="Reset the values to initial values")
    cp.register_command("print", plot.print, helpmsg="Print the set values")
    cp.register_command("export_text", plot.export_readable, args=["file"], helpmsg="Export all the values to a file in readable format")
    cp.register_command("export_csv", plot.export_csv, args=["file"], helpmsg="Export all the values to a file in csv format")
    cp.register_command("import_csv", plot.import_csv, args=["file"], helpmsg="Import all the values from a file in csv format")
    cp.register_command("order", plot.print_order, helpmsg="Print the standard order of the valves")
    cp.register_command("play", plot.play_audio, args=["duration"], helpmsg="Play the sound for <duration> seconds")
    cp.register_command("stop_audio", plot.stop_audio, helpmsg="Stop the playing sound")
    # cp.register_command("add", plot.add_valve, args=["name"], helpmsg="Add another valve noise to the model")
    
    # Add refresh handlers for graph
    cp.register_action_after_symbolic(plot.update_original)
    cp.register_action_after_symbolic(plot.update_model)
    
    # Create the general settings
    general_group = cp.register_symbolic_group("General", "Contains specs and props for general purposes")
    cp.register_symbolic_spec("G", general_group, lambda: plot, "General settings on the plot object")
    
    cp.register_symbolic_prop("BPM", general_group, lambda obj: obj.model.BPM, lambda obj, val: setattr(obj, "BPM", val), dtype=int, helpmsg="The BPM of the heart signal")
    cp.register_symbolic_prop("shift", general_group, lambda obj: obj.originalSound.shift, lambda obj, val: setattr(obj, "shift", val), dtype=float, helpmsg="The BPM of the heart signal")
    cp.register_symbolic_prop("n", general_group, lambda obj: obj.model.n, lambda obj, val: setattr(obj, "n", val), dtype=int, helpmsg="The amount of times the signal is repeated")
    
    valve_group = cp.register_symbolic_group("Valves", "Contains specs and props for the valves. Order: M, T, A, P")
    for valve in plot.model.valves:
        cp.register_symbolic_spec(valve.name, valve_group, lambda v=valve: v, helpmsg=f"The {valve.name} peak")
        
    cp.register_symbolic_prop("delay", valve_group, lambda obj: obj.delay * 1000, lambda obj, val: setattr(obj, "delay", val/1000), dtype=float, helpmsg="The delay before the valve sound starts in ms")
    
    cp.register_symbolic_prop("durtot", valve_group, lambda obj: obj.duration_total * 1000, lambda obj, val: setattr(obj, "duration_total", val/1000), dtype=float, helpmsg="The duration of the total valve sound in ms")
    cp.register_symbolic_prop("duron", valve_group, lambda obj: obj.duration_onset * 1000, lambda obj, val: setattr(obj, "duration_onset", val/1000), dtype=float, helpmsg="The duration of the onset of the valve sound in ms. Should be greater than 'totdur'")
    
    cp.register_symbolic_prop("gainon", valve_group, lambda obj: obj.a_onset, lambda obj, val: setattr(obj, "a_onset", val), dtype=float, helpmsg="The a (gain) of the onset")
    cp.register_symbolic_prop("gain", valve_group, lambda obj: obj.a_main, lambda obj, val: setattr(obj, "a_main", val), dtype=float, helpmsg="The a (gain) of the main signal")
    
    cp.register_symbolic_prop("amplon", valve_group, lambda obj: obj.ampl_onset, lambda obj, val: setattr(obj, "ampl_onset", val), dtype=float, helpmsg="The amplitude of the onset")
    cp.register_symbolic_prop("ampl", valve_group, lambda obj: obj.ampl_main, lambda obj, val: setattr(obj, "ampl_main", val), dtype=float, helpmsg="The amplitude of the main signal")
        
    
    cp.register_symbolic_prop("freqon", valve_group, lambda obj: obj.freq_onset, lambda obj, val: setattr(obj, "freq_onset", val), dtype=float, helpmsg="The frequency of the onset of the valve sound in Hz")
    cp.register_symbolic_prop("freq", valve_group, lambda obj: obj.freq_main, lambda obj, val: setattr(obj, "freq_main", val), dtype=float, helpmsg="The frequency of the main valve sound in Hz")

    return cp