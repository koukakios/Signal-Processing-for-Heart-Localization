from lib.config.ConfigParser import ConfigParser
from src.module_2.generate import *
from os.path import join
from scipy.io.wavfile import write
import matplotlib.pyplot as plt
from src.module_2.plot import Plot

config = ConfigParser()
n = config.HeartSoundModel.NBeats
Fs = config.HeartSoundModel.Fs

plot = Plot("", config, log_enabled=False, disable_orignal=True)
plot.import_csv(".\\src\\module_2\\quite_good_params.csv", run_plot=False)
t_model, h_model, _, _ = plot.get_model()
write(join(config.Generation.SoundsPath, f"Advanced-{Fs}Hz-{plot.BPM}BPM-{n} beats.wav"), Fs, h_model)