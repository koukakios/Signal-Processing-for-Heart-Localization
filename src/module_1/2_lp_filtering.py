import numpy as np
import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from lib.config.ConfigParser import ConfigParser
from lib.preprocessing.functions import construct_filter
from lib.preprocessing.PreProcessor import PreProcessor

def assignment422(config: ConfigParser, Fs: int=48e3):
    """Executes assignment 4.2.2.

    Args:
        config (ConfigParser): The config object.
        Fs (int, optional): The desired sampling frequency of the filter in Hz. Defaults to 48e3.
    """
    g = construct_filter(
        config.LowpassFilter.LowFrequency, 
        config.LowpassFilter.HighFrequency, 
        Fs, 
        order=config.LowpassFilter.FilterOrder,
        size=config.LowpassFilter.Size
    )

    freq, damping = np.abs(getDamping(g, 2000, Fs, 1000000))
    print(f"Damping at {freq:.1f} Hz is {todB(damping):.2f} dB")
    
    fig, ax = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)
    timeFrequencyPlot(
        g, 
        Fs, 
        ax[0], 
        ax[1], 
        samples_offset = -len(g)/2, 
        apply_fftshift=True
    )
    fig.suptitle("Non-causal butterworth bandpass filter $g(t)$")
    plt.show()
    
def assignment423(config: ConfigParser):
    """Executes assignment 4.2.3.

    Args:
        config (ConfigParser): The config object.
    """
    file_path = ".\\samples\\stethoscope_5_realHeart_\\recording_2025-07-10_14-40-12_channel_1.wav"
    
    processor = PreProcessor(file_path, config, save_results=True)
    processor.process()
    print(f"Fs is {processor.Fs_original} Hz")
    
    fig, ax = plt.subplots(2, 2, figsize=(8,4), constrained_layout=True)
    timeFrequencyPlot(
        processor.x, 
        processor.Fs_original, 
        ax[0][0], 
        ax[0][1], 
        apply_fftshift=True, 
        time_title="Time domain of recording", 
        freq_title="Frequency domain of recording"
    )
    timeFrequencyPlot(
        processor.y, 
        processor.Fs_original, 
        ax[1][0], 
        ax[1][1], 
        samples_offset = -len(processor.g)/2, 
        apply_fftshift=True, 
        time_title="Time domain of filtered recording", 
        freq_title="Frequency domain of filtered recording"
    )
    
    ax[0][0].sharex(ax[1][0])
    ax[0][1].sharex(ax[1][1])
    
    plt.show()
    
def main():
    """The main loop. Can be changed to choose whether to run assignment 4.2.2 or 4.2.3.
    """
    config = ConfigParser()
    assignment422(config)
    assignment423(config)

if __name__ == "__main__":
    main()