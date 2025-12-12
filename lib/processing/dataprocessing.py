from scipy import signal
import numpy as np
from enum import Enum
from typing import Callable

class HeartSound (Enum):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    S1 = 0
    S2 = 1

def get_peaks(x: np.ndarray, min_height: float, min_dist: float):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    peaks, properties = signal.find_peaks(x, height=min_height, distance=min_dist)

    return peaks, properties

def get_dist_peaks_to_next(x_peaks: np.ndarray):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    diff = np.diff(x_peaks)
    return dict(zip(x_peaks[:-1], diff))

def remove_outliers(x: list[tuple[int, int]]):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
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
    """
    @author: Gerrald
    @date: 10-12-2025
    """
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
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    raise NotImplementedError()
    diff = np.diff(x_peaks)
    diff2 = np.diff(diff)
    
    s2_peaks, s2_outliers, s1_peaks, s1_outliers = analyze_diff2(x_peaks, diff, diff2)
    
    return np.array(s1_peaks), np.array(s2_peaks), np.array(s1_outliers), np.array(s2_outliers)

def pop_np(x):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    return x[-1], x[:-1]

def get_difference(a,b):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    a_rows = {tuple(row) for row in a}
    b_rows = {tuple(row) for row in b}
    
    return list(a_rows - b_rows)

def detect_peak_domains(peaks: np.ndarray, see: np.ndarray, threshold: float):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    peak_start = None
    peaks_ind = []
    for i, s in enumerate(see):
        if s >= threshold and peak_start is None:
            peak_start = i
        elif s <= threshold and peak_start is not None:
            if np.any((peaks[:,0] >= peak_start) & (peaks[:,0] <= i)):
                peaks_ind.append((peak_start, i))
            peak_start = None
    return np.array(peaks_ind)

def segment_only_with_len_filter_and_thus_deprecated_should_not_be_used(signal: np.ndarray, domains: np.ndarray, len_filter: int):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    mask = np.zeros(len(signal), dtype=bool)
    comp = int(len_filter / 2)
    for start, end in domains:
        mask[start - comp:end - comp] = True
    return np.where(mask, signal, 0)

def segment(signal: np.ndarray, domains: np.ndarray, comp: Callable[[int], int]):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    mask = np.zeros(len(signal), dtype=bool)
    concatenated = []
    for start, end in domains:
        mask[comp(start):comp(end)] = True
        concatenated.extend(signal[comp(start):comp(end)])
    return np.where(mask, signal, 0), np.array(concatenated) 