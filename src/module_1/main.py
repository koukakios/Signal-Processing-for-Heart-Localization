from config import *
from scipy import signal
from scipy.fft import fft
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from functions import construct_filter

def filter(x: list|np.ndarray, g: list|np.ndarray):
    return np.convolve(x, g)

def downsample(x, Fs_original):
    M = Fs_original / Fs
    
    if int(M) != M:
        print(f"ERROR: M is not an integer: {Fs_original}/{Fs}={M:.5f}")
        raise ValueError(f"ERROR: M is not an integer: {Fs_original}/{Fs}={M:.5f}")
    
    M = int(M)
    x_downsampled = x[::M]
    
    return x_downsampled

def preprocess():
    Fs_original, x = wavfile.read(".\\samples\\stethoscope_5_realHeart_\\recording_2025-07-10_14-40-12_channel_1.wav")
    
    g = construct_filter(LP_low_freq, LP_high_freq, Fs_original, order=LP_filter_order)
    
    y = filter(x, g)
    
    y_downsampled = downsample(x, Fs_original)

    
def main():
    preprocess()
    

if __name__ == "__main__":
    main()