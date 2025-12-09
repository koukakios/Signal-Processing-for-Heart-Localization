import numpy as np
import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.plot.spectogramPlot import spectogramPlot
from lib.general.generalUtils import todB
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter
from lib.processing.Processor import Processor
from scipy.io import wavfile
from pathlib import Path

def assignment441(config):
    path = ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-05_channel_5.wav"
    Fs, x = wavfile.read(path)
    
    t = np.linspace(0, len(x)/Fs, len(x))
    fig, ax = plt.subplots(1, 2, figsize=(8, 4), constrained_layout=True)
    spectogramPlot(x, Fs, ax[0], title=f"Spectogram of {Path(path).name}")
    ax[1].plot(t, x)
    ax[1].set_title(f"Time domain of {Path(path).name}")
    ax[1].grid()
    ax[1].set_xlabel("Time[s]")
    ax[1].set_ylabel("Amplitude")
    
    
    plt.show()


def main():
    """The main loop. Can be changed to choose whether to run assignment 4.4.2 or 4.4.3.
    """
    config = ConfigParser()
    assignment441(config)

if __name__ == "__main__":
    main()