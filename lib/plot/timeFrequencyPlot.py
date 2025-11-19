import matplotlib.pyplot as plt
from matplotlib import axes
from scipy.fft import fft, fftshift
import numpy as np
from lib.general.generalUtils import todB

def timeFrequencyPlot(x: list|np.ndarray, Fs: int, time_ax: axes.Axes, freq_ax: axes.Axes, time_title:str=None, freq_title:str=None, grid: bool = True, samples_offset: float = 0, apply_fftshift:bool=False, resolution: int|None = None):
    if resolution is not None:
        X = fft(x, resolution)
    else:
        X = fft(x)
    
    t = np.linspace(0 + samples_offset/Fs, (len(x) + samples_offset)/Fs, len(x))
    
    if apply_fftshift:
        X = fftshift(X)
        f = np.linspace(-Fs/2, Fs/2, len(X))
    else:
        f = np.linspace(0, Fs, len(X))
    
    time_ax.plot(t, x)
    time_ax.set_xlabel("Time [s]")
    time_ax.set_ylabel("Amplitude")
    
    freq_ax.plot(f, todB(np.abs(X)))
    freq_ax.set_xlabel("Frequency [Hz]")
    freq_ax.set_ylabel("Amplitude(dB)")
    
    time_ax.grid(grid)
    freq_ax.grid(grid)
    
    if time_title is not None:
        time_ax.set_title(time_title)
    if freq_title is not None:
        freq_ax.set_title(freq_title)
