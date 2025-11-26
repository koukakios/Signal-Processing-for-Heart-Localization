from scipy import signal
import numpy as np
from enum import Enum

class HeartSound (Enum):
    S1 = 0
    S2 = 1

def get_peaks(x: np.ndarray, min_height: float, min_dist: float):
    peaks, properties = signal.find_peaks(x, height=min_height, distance=min_dist)

    return peaks, properties

def get_dist_peaks_to_next(x_peaks: np.ndarray):
    diff = np.diff(x_peaks)
    return dict(zip(x_peaks[:-1], diff))

def remove_outliers(x: list[tuple[int, int]]):
    x = np.array(x)
    dist = x[:,1]
    Q1 = np.percentile(dist, 25)
    Q3 = np.percentile(dist, 75)
    
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    outliers = x[(dist < lower_bound) | (dist > upper_bound)]
    data = x[(dist >= lower_bound) & (dist <= upper_bound)]
    
    return data, outliers

def analyze_diff2(x_peaks: np.ndarray, diff: np.ndarray, diff2: np.ndarray):
    minima = []
    maxima = []
    uncertain = []
    previous_d = None
    for i, peak, d in zip(range(len(x_peaks)-1), x_peaks[:-1], [*diff2, None]):
        to_add = (peak, diff[i])
        if d is None and previous_d is None:
            if minima[-1] > maxima[-1]: maxima.append(to_add)
            else: minima.append(to_add)
        elif (d is None or d < 0) and (previous_d is None or previous_d > 0):
            maxima.append(to_add)
        elif (d is None or d >= 0) and (previous_d is None or previous_d <= 0):
            minima.append(to_add)
        else:
            uncertain.append(to_add)
        previous_d = d
            
    maxima, max_outliers = remove_outliers(maxima)
    minima, min_outliers = remove_outliers(minima)
    
    return maxima, max_outliers, minima, min_outliers

def classify_peaks(x_peaks: np.ndarray):
    raise NotImplementedError()
    diff = np.diff(x_peaks)
    diff2 = np.diff(diff)
    
    s2_peaks, s2_outliers, s1_peaks, s1_outliers = analyze_diff2(x_peaks, diff, diff2)
    
    return np.array(s1_peaks), np.array(s2_peaks), np.array(s1_outliers), np.array(s2_outliers)

def pop_np(x):
    return x[-1], x[:-1]