from config import *
from scipy import signal
from scipy.fft import fft
import numpy as np
import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from math import floor

def construct_filter(low: float, high: float, Fs: int, order: int = 2):
    b, a = signal.butter(order, [2*low/Fs, 2*high/Fs], btype="band")
    g = signal.filtfilt(b, a, [*np.zeros(10000), 1, *np.zeros(10000)])
    return g

def filter(b, a, data):
    return signal.filtfilt(b, a, data)

def main():
    Fs = 48e3
    g = construct_filter(10, 800, Fs)

    fig, ax = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)
    timeFrequencyPlot(g, Fs, ax[0], ax[1], samples_offset = -len(g)/2, apply_fftshift=True, resolution=None)
    fig.suptitle("Non-causal butterworth bandpass filter $g(t)$")
    plt.show()

if __name__ == "__main__":
    main()