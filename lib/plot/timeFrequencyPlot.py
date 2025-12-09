import matplotlib.pyplot as plt
from matplotlib import axes
from scipy.fft import fft, fftshift
import numpy as np
from lib.general.generalUtils import todB

def timeFrequencyPlot(x: list|np.ndarray, Fs: int, time_ax: axes.Axes, freq_ax: axes.Axes, time_title:str=None, freq_title:str=None, grid: bool = True, samples_offset: float = 0, apply_fftshift:bool=False, resolution: int|None = None, freq_label: str="", time_label: str=""):
    """Plots the time and frequency spectrum of an input signal x.

    Args:
        x (list | np.ndarray): The input signal.
        Fs (int): The original sampling rate.
        time_ax (axes.Axes): The matplotlib.axes.Axes object to plot the time spectrum on.
        freq_ax (axes.Axes): The matplotlib.axes.Axes object to plot the frequency spectrum on.
        time_title (str, optional): The title of the time spectrum plot. Defaults to None.
        freq_title (str, optional): The title of the frequency spectrum plot. Defaults to None.
        grid (bool, optional): Whether to show a grid in the plots. Defaults to True.
        samples_offset (float, optional): How many samples the time input array begins at.. Defaults to 0.
        apply_fftshift (bool, optional): Whether to apply an fftshift, so plot from -Fs/2 to Fs/2. Defaults to False.
        resolution (int | None, optional): The resolution of the fft. If None, the result will be as long as the input signal. Defaults to None.
        freq_label (str, optional): The label of the frequency spectrum plot. Defaults to None.
        time_label (str, optional): The label of the time spectrum plot. Defaults to None.
    """
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
    
    time_ax.plot(t, x, label=time_label)
    time_ax.set_xlabel("Time [s]")
    time_ax.set_ylabel("Amplitude")
    
    freq_ax.plot(f, todB(np.abs(X)), label=freq_label)
    freq_ax.set_xlabel("Frequency [Hz]")
    freq_ax.set_ylabel("Amplitude(dB)")
    
    time_ax.grid(grid)
    freq_ax.grid(grid)
    
    if time_title is not None:
        time_ax.set_title(time_title)
    if freq_title is not None:
        freq_ax.set_title(freq_title)
