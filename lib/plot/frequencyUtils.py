import matplotlib.pyplot as plt
from matplotlib import axes
from scipy.fft import fft, fftshift
import numpy as np

def getDamping(x: list|np.ndarray, freq:int, Fs: int, resolution: int|None = None):
    """
    @author: Gerrald
    @date: 10-12-2025

    Get the damping of a transfer function x at freq Hz.

    Args:
        x (list | np.ndarray): The transfer function of the filter.
        freq (int): The frequency we want to know the damping of.
        Fs (int): The original sampling frequency in Hz.
        resolution (int | None, optional): The resolution of the fft transform. If it is None, it is the length of x. Defaults to None.

    Returns:
        (float, float): The frequency the damping was measured on. Can be a little different from the requested frequency. Increase resolution for a better approximation. The second argument is the damping (linear) at the given frequency.
    
    """
    if resolution is not None:
        X = fft(x, resolution)
    else:
        X = fft(x)
    
    index = round(freq * len(X) / Fs)
    
    return (index * Fs / len(X), 1/X[index])