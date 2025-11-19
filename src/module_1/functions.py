from config import *
from scipy import signal
from scipy.fft import fft
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB

def construct_filter(low: float, high: float, Fs: int, order: int = 2):
    b, a = signal.butter(order, [2*low/Fs, 2*high/Fs], btype="band")
    g = signal.filtfilt(b, a, [*np.zeros(LP_resolution), 1, *np.zeros(LP_resolution)])
    return g
