from scipy import signal
import numpy as np
from math import floor

def get_peaks(x: np.ndarray, min_height: float, min_dist: float):
    peaks, properties = signal.find_peaks(x, height=min_height, distance=min_dist)

    return peaks, properties

def get_dist_peaks_to_next(x_peaks: np.ndarray):
    diff = np.diff(x_peaks)
    return dict(zip(x_peaks[:-1], diff))