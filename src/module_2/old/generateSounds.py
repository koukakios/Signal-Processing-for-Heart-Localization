from lib.config.ConfigParser import ConfigParser
from lib.model.generate import *
from os.path import join
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from src.module_2.plot import Plot


def generateSounds(config: ConfigParser, valves: list[ValveParams]|None = None, write_enabled: bool = True, randomize: bool = False):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    n = config.HeartSoundModel.NBeats
    Fs = config.HeartSoundModel.Fs

    plot = Plot("", config, log_enabled=False, disable_orignal=True)
    plot.import_csv(".\\src\\module_2\\model_params.csv", run_plot=False)
    
    if valves is None:
        valves = plot.valves    
    
    t_model, h_model = advanced_model(
        Fs,
        plot.BPM,
        plot.lf,
        plot.hf,
        plot.order,
        plot.size,
        valves,
        n,
        randomize_enabled = randomize,
        r_ratio = 0.05,
        bpm_ratio = 0.2
    ) 
    if write_enabled:
        write(join(config.Generation.SoundsPath, f"Advanced-{Fs}Hz-{plot.BPM}BPM-{n} beats.wav"), Fs, h_model)
        
    return h_model, Fs