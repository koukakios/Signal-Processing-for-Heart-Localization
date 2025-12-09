import numpy as np
import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter
from lib.processing.Processor import Processor

def result45(config):
    path = ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav"
    processor = Processor(path, config, save_steps=True)
    
    processor.process()
    
    fig, ax = plt.subplots(4, 2, figsize=(8,12), constrained_layout=True)
    timeFrequencyPlot(
        processor.x, 
        processor.Fs_original, 
        ax[0][0], 
        ax[0][1], 
        apply_fftshift=True, 
        samples_offset=len(processor.g)/2,
        time_title="Time domain of recording", 
        freq_title="Frequency domain of recording"
    )
    
    timeFrequencyPlot(
        processor.y_downsampled, 
        processor.Fs_target, 
        ax[1][0], 
        ax[1][1], 
        apply_fftshift=True, 
        time_title="Time domain of processed recording", 
        freq_title="Frequency domain of processed recording"
    )
    
    timeFrequencyPlot(
        processor.y_normalized, 
        processor.Fs_target, 
        ax[2][0], 
        ax[2][1], 
        apply_fftshift=True, 
        time_title="Time domain of processed and normalized recording", 
        freq_title="Frequency domain of processed and normalized recording"
    )
    
    timeFrequencyPlot(
        processor.y_energy, 
        processor.Fs_target, 
        ax[3][0], 
        ax[3][1], 
        apply_fftshift=True, 
        time_title="Signal energy of recording", 
        freq_title="Frequency domain of Shannon energy",
        freq_label="Shannon energy",
        time_label="Shannon energy"
    )
    timeFrequencyPlot(
        processor.see, 
        processor.Fs_target, 
        ax[3][0], 
        ax[3][1], 
        apply_fftshift=True,
        samples_offset=-len(processor.see_filter)/2,
        freq_label="Shannon energy envelope",
        time_label="Shannon energy envelope"
    )
    ax[3][0].legend()
    ax[3][1].legend()
    
    # Share axes
    master_ax = ax[0, 0]
    for row in range(1, 4):
        ax[row, 0].sharex(master_ax)
        
    master_ax = ax[1, 1]
    for row in range(2, 4):
        ax[row, 1].sharex(master_ax)
    
    plt.show()
    
def filter45(config):
    path = ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav"
    processor = Processor(path, config, save_steps=True)
    
    processor.process()

    fig, ax = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)
    
    timeFrequencyPlot(
        processor.see_filter, 
        processor.Fs_target, 
        ax[0], 
        ax[1], 
        apply_fftshift=True,
        samples_offset=-len(processor.see_filter)/2,
        time_title="Time domain of Shannon Envelope Filter", 
        freq_title="Frequency domain of Shannon Envelope Filter"
    )
    plt.show()

def main():
    """The main loop. Can be changed to choose whether to run assignment 4.2.2 or 4.2.3.
    """
    config = ConfigParser()
    filter45(config)

if __name__ == "__main__":
    main()