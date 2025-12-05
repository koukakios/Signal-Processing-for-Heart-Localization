import numpy as np
import matplotlib.pyplot as plt
from lib.config.ConfigParser import ConfigParser
import sounddevice as sd
from lib.processing.Processor import Processor
from src.module_2.generate import *
import matplotlib as mpl
import re
from copy import deepcopy

mpl.use('qtagg')
mpl.rcParams["path.simplify"] = True
mpl.rcParams["path.simplify_threshold"] = 1
plt.ion()

def getData():
    config = ConfigParser()

    t_model, h_model = advanced_model(config) 
    
    return t_model, h_model

def timeOriginal(shift, length, Fs):
    return np.linspace(shift, shift+length/Fs, length)
    
def getCommand(cmd: str, general_specifiers: list, general_props: list, peak_specifiers: list, peak_props: list):
    pattern = fr"^((?P<specg>[{''.join(general_specifiers)}])\s+(?P<propg>{'|'.join(general_props)})\s+(?P<valg>[\-0-9.,_]+)|"+\
        fr"(?P<specp>[{''.join(peak_specifiers)}])\s+(?P<propp>{'|'.join(peak_props)})\s+(?P<valp>[\-0-9.,_]+))$"
    m = re.match(pattern, cmd)
    if m:
        spec = m.group("specg") or m.group("specp")
        prop = m.group("propg") or m.group("propp")
        val = m.group("valg") or m.group("valp")
        return spec, prop, val.replace(",", ".").replace("_", "")
    return False

def matchParams():
    config = ConfigParser()
    Fs = config.HeartSoundModel.Fs
    len_g = config.LowpassFilter.Size
    lf = config.LowpassFilter.LowFrequency
    hf = config.LowpassFilter.HighFrequency
    order=config.LowpassFilter.FilterOrder
    size=config.LowpassFilter.Size
    
    # Define params
    n = n_init = config.HeartSoundModel.NBeats
    BPM = BPM_init = config.HeartSoundModel.BPM
    shift = shift_init = -2.28
    valves_init = [
        ValveParams( 10, 30, 10, 10, 0.05, 0.1,   1,  50,  50, "M"), 
        ValveParams( 40, 30, 10, 10, 0.05, 0.1, 0.5, 150, 150, "T"), 
        ValveParams(300, 30, 10, 10, 0.05, 0.1, 0.5,  50,  50, "A"), 
        ValveParams(330, 30, 10, 10, 0.05, 0.1, 0.4,  30,  30, "P"), 
    ]
    
    valves = deepcopy(valves_init)
    
    # Get original heart sound
    processor = Processor("samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav", config, save_steps=True, write_result_processed=False, write_result_raw=False)
    processor.process()
    
    t_model, h_model = advanced_model(
        Fs,
        BPM,
        lf,
        hf,
        order,
        size,
        valves,
        n
    ) 
    
    fig, ax = plt.subplots()    
    min_t = min(t_model)-0.1
    max_t = max(t_model)+0.1
    modelplot, = ax.plot(t_model, h_model, label="Model")
    
    original, = ax.plot(timeOriginal(shift_init, len(processor.y_normalized), processor.Fs_target), processor.y_normalized, label="Real data")
    ax.set_xlim(min_t, max_t)
    ax.set_title("Advanced")
    ax.legend()
    ax.grid(True)
    
    def updateOriginal(shift):
        t = timeOriginal(shift, len(processor.y_normalized), processor.Fs_target)
        original.set_xdata(t)
        fig.canvas.draw_idle()
        
    def updateModel(BPM, n, valves):
        t_model, h_model = advanced_model(
            Fs,
            BPM,
            lf,
            hf,
            order,
            size,
            valves,
            n
        ) 
        modelplot.set_xdata(t_model)
        modelplot.set_ydata(h_model)
        fig.canvas.draw_idle()

    
    
    # Interactive menu
    peak_props = [
        prop for prop in dir(valves_init[0])
        if not prop.startswith("_") and prop not in ["name", "toStr"]
    ]
    names = [valve.name for valve in valves]
    general_props = ["BPM", "shift", "n"]
    general_specs = ["G"]
    
    def print_specs():
        print(f"Specifiers:\n  - General: G\n  - Peaks: {', '.join(names)}")
    def print_props():
        print(f"Props:\n  - General: {', '.join(general_props)}\n  - Peaks: {', '.join(peak_props)}")
    def print_vals(BPM, shift, valves):
        print(f"""Original:\n  - shift: {shift}s\nModel:\n  - BPM: {BPM}\n  - Valves:""")
        for valve in valves:
            print("  - " + "\n    ".join(valve.toStr()))
    def print_help():
        print(f"""Help:

Normal usage: 
<specifier> <prop> <value>

Commands:
- help: show this menu
- exit: exit the graph
- reset: reset all params
- opt: print all options
- specs: print all specifiers
- props: print the props that can be changed
- print: print set values
- play: play the generated sound""")
        
    
    while True:
        cmd = input("> ").strip()
        if cmd == "":
            continue
        elif result := getCommand(cmd, general_specs, general_props, names, peak_props):
            spec, prop, val = result
            success = True
            if spec in general_specs:
                if spec == "G":
                    if prop == "BPM":
                        try:
                            BPM = int(val)
                        except:
                            success = False
                            print("BPM must be an int")
                    elif prop == "shift":
                        try:
                            shift = float(val)
                        except:
                            success = False
                            print("shift must be a float")
                    elif prop == "n":
                        try:
                            n = int(val)
                        except:
                            success = False
                            print("n must be an int")
                    else:
                        raise NotImplementedError
                else:
                    raise NotImplementedError
                if success:
                    updateOriginal(shift)
                    updateModel(BPM, n, valves)
            else:
                try:
                    setattr(valves[names.index(spec)], prop, float(val) / (1000 if prop in ["delay", "duration", "onset"] else 1))
                except:
                    success = False
                    print("Value not castable to float")
                if success:
                    updateModel(BPM, n, valves)
        else:
            match cmd:
                case "exit":
                    return
                case "opt":
                    print_specs()
                    print_props()
                case "specs":
                    print_specs()
                case "props":
                    print_props()
                case "help":
                    print_help()
                case "reset":
                    BPM = BPM_init
                    n = n_init
                    shift = shift_init
                    valves = deepcopy(valves_init)
                    updateModel(BPM, n, valves)
                    updateOriginal(shift)
                case "print":
                    print_vals(BPM, shift, valves)
                case "play":
                    t_model, h_model = advanced_model(
                        Fs,
                        BPM,
                        lf,
                        hf,
                        order,
                        size,
                        valves,
                        n
                    ) 
                    sd.play(h_model, Fs)
                case _:
                    print(f"{cmd} is an unknown command. Use `help` to view the help menu")
        



if __name__ == "__main__":
    matchParams()
    
# sample values:
# Original:
#   - shift: -2.2s
# Model:
#   - BPM: 65
#   - Valves:
#   - Name: M
#       Duration: 75.0ms
#       Frequency: 26.0Hz
#       Amplitude: 0.7
#       Delay: 5.0ms
#       Onset: 12.0ms
#   - Name: T
#       Duration: 50.0ms
#       Frequency: 10.0Hz
#       Amplitude: 0.5
#       Delay: 55.0ms
#       Onset: 50.0ms
#   - Name: A
#       Duration: 55.0ms
#       Frequency: 35.0Hz
#       Amplitude: 0.7
#       Delay: 325.0ms
#       Onset: 20.0ms
#   - Name: P
#       Duration: 30.0ms
#       Frequency: 16.0Hz
#       Amplitude: 0.4
#       Delay: 400.0ms
#       Onset: 0.0ms