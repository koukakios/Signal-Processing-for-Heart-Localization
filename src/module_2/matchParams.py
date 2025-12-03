from scipy.signal import TransferFunction, impulse, zpk2tf
import numpy as np
import matplotlib.pyplot as plt
from lib.config.ConfigParser import ConfigParser
import sounddevice as sd
from lib.processing.Processor import Processor
from lib.processing.functions import construct_bandpass_filter, apply_filter
from os.path import join
from scipy.io.wavfile import write
from src.module_2.generate import *
import matplotlib as mpl
from matplotlib.widgets import Button, Slider, TextBox
from math import ceil, floor
import re
from copy import deepcopy

# mpl.use('qtagg')
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
    n = config.HeartSoundModel.NBeats
    len_g = config.LowpassFilter.Size
    lf = config.LowpassFilter.LowFrequency
    hf = config.LowpassFilter.HighFrequency
    order=config.LowpassFilter.FilterOrder
    size=config.LowpassFilter.Size
    
    # Define params
    BPM = BPM_init = config.HeartSoundModel.BPM
    shift = shift_init = -2.28
    valves_init = [
        ValveParams(20,  50,   1,  10, 10, "M"),
        ValveParams(20, 150, 0.5,  40, 10, "T"),
        ValveParams(20,  50, 0.5, 300, 10, "A"),
        ValveParams(20,  30, 0.4, 330, 10, "P"),
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
        valves_init
    ) 
    
    fig, ax = plt.subplots()    
    min_t = min(t_model)-0.1
    max_t = max(t_model)+0.1
    modelplot, = ax.plot(t_model, h_model, label="Model")
    
    t = timeOriginal(shift_init, len(processor.y_normalized), processor.Fs_target)
    mask = (t >= min_t) & (t <= max_t)
    
    original, = ax.plot(t[mask], processor.y_normalized[mask], label="Real data")
    ax.set_xlim(min_t, max_t)
    ax.set_title("Advanced")
    ax.legend()
    ax.grid(True)
    
    def updateOriginal(shift):
        t = timeOriginal(shift, len(processor.y_normalized), processor.Fs_target)
        mask = (t >= min_t) & (t <= max_t)
        original.set_xdata(t[mask])
        original.set_ydata(processor.y_normalized[mask])
        fig.canvas.draw_idle()
        
    def updateModel(BPM, valves):
        _, h_model = advanced_model(
            Fs,
            BPM,
            lf,
            hf,
            order,
            size,
            valves
        ) 
        modelplot.set_ydata(h_model)
        fig.canvas.draw_idle()

    
    
    # Interactive menu
    peak_props = [
        prop for prop in dir(valves_init[0])
        if not prop.startswith("_") and prop not in ["name", "toStr"]
    ]
    names = [valve.name for valve in valves]
    general_props = ["BPM", "shift"]
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
- print: print set values""")
        
    
    while True:
        cmd = input("> ").strip()
        if result := getCommand(cmd, general_specs, general_props, names, peak_props):
            spec, prop, val = result
            success = True
            if spec in general_specs:
                if spec == "G":
                    if prop == "BPM":
                        try:
                            BPM = int(val)
                        except:
                            success = False
                            print("BPM must be a int")
                    elif prop == "shift":
                        try:
                            shift = float(val)
                        except:
                            success = False
                            print("BPM must be a int")
                    else:
                        raise NotImplementedError
                else:
                    raise NotImplementedError
                if success:
                    updateOriginal(shift)
            else:
                try:
                    setattr(valves[names.index(spec)], prop, float(val) / (1000 if prop in ["delay", "duration", "onset"] else 1))
                except:
                    success = False
                    print("Value not castable to float")
                if success:
                    updateModel(BPM, valves)
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
                    shift = shift_init
                    valves = deepcopy(valves_init)
                    updateModel(BPM, valves)
                    updateOriginal(shift)
                case "print":
                    print_vals(BPM, shift, valves)
                case _:
                    print(f"{cmd} is an unknown command. Use `help` to view the help menu")
        



if __name__ == "__main__":
    matchParams()