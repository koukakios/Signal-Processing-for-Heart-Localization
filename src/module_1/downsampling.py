from config import *
from scipy import signal
from scipy.fft import fft
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from functions import *
from main import *

def assignment431():
    Fs_original = 48e3
    Fs_target = 4e3
    print(f"The downsampling factor M should be {Fs_original / Fs_target:.0f}")

def assignment432():
    Fs_original, x = wavfile.read(".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav")
    
    g = construct_filter(LP_low_freq, LP_high_freq, Fs_original, order=LP_filter_order)
    
    y = filter(x, g)
    
    y_downsampled = downsample(x, Fs_original)
    
    fig, ax = plt.subplots(2, 2, figsize=(8,4), constrained_layout=True)
    timeFrequencyPlot(x, Fs_original, ax[0][0], ax[0][1], apply_fftshift=True, time_title="Time domain of recording", freq_title="Frequency domain of recording")
    timeFrequencyPlot(y_downsampled, Fs, ax[1][0], ax[1][1], samples_offset = -len(g)/2, apply_fftshift=True, time_title="Time domain of processed recording", freq_title="Frequency domain of processed recording")
    ax[0][0].sharex(ax[1][0])
    
    plt.show()

def main():
    assignment432()
    
if __name__ == "__main__":
    main()