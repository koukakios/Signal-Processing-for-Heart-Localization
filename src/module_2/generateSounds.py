from lib.config.ConfigParser import ConfigParser
from src.module_2.generate import *
from os.path import join
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from src.module_2.plot import Plot


def generateSounds(config: ConfigParser, valves: list[ValveParams]|None = None, write_enabled: bool = True):
    n = config.HeartSoundModel.NBeats
    Fs = config.HeartSoundModel.Fs

    plot = Plot("", config, log_enabled=False, disable_orignal=True)
    plot.import_csv(".\\src\\module_2\\quite_good_params.csv", run_plot=False)
    
    if valves is not None:
        plot.valves = valves
    
    t_model, h_model, _, _ = plot.get_model()
    if write_enabled:
        write(join(config.Generation.SoundsPath, f"Advanced-{Fs}Hz-{plot.BPM}BPM-{n} beats.wav"), Fs, h_model)
        
    return h_model, Fs