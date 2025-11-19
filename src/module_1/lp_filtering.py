from config import *
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from functions import construct_filter

def assignment422():
    Fs = 48e3
    g = construct_filter(LP_low_freq, LP_high_freq, Fs, order=LP_filter_order)

    freq, damping = np.abs(getDamping(g, 2000, Fs, 1000000))
    print(f"Damping at {freq:.1f} Hz is {todB(damping):.2f} dB")
    
    fig, ax = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)
    timeFrequencyPlot(g, Fs, ax[0], ax[1], samples_offset = -len(g)/2, apply_fftshift=True)
    fig.suptitle("Non-causal butterworth bandpass filter $g(t)$")
    plt.show()
    
def assignment423():
    Fs, x = wavfile.read(".\\samples\\stethoscope_5_realHeart_\\recording_2025-07-10_14-40-12_channel_1.wav")
    print(f"Fs is {Fs} Hz")
    g = construct_filter(LP_low_freq, LP_high_freq, Fs, order=LP_filter_order)
    
    y = np.convolve(x, g)
    
    fig, ax = plt.subplots(2, 2, figsize=(8,4), constrained_layout=True)
    timeFrequencyPlot(x, Fs, ax[0][0], ax[0][1], apply_fftshift=True, time_title="Time domain of recording", freq_title="Frequency domain of recording")
    timeFrequencyPlot(y, Fs, ax[1][0], ax[1][1], samples_offset = -len(g)/2, apply_fftshift=True, time_title="Time domain of filtered recording", freq_title="Frequency domain of filtered recording")
    
    ax[0][0].sharex(ax[1][0])
    ax[0][1].sharex(ax[1][1])
    
    plt.show()
    
def main():
    assignment422()

if __name__ == "__main__":
    main()