import numpy as np
import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter
from lib.processing.Processor import Processor
from lib.processing.dataprocessing import HeartSound

def segmentation(config):
    path = ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav"
    processor = Processor(path, config, save_results=True)
    
    processor.process()
    
    fig, ax = plt.subplots(3, 2, figsize=(8,6), constrained_layout=True)
    
    timeFrequencyPlot(
        processor.y_energy, 
        processor.Fs_target, 
        ax[0][0], 
        ax[0][1], 
        samples_offset=len(processor.see_filter)/2,
        apply_fftshift=True,
    )
    timeFrequencyPlot(
        processor.see, 
        processor.Fs_target, 
        ax[0][0], 
        ax[0][1], 
        apply_fftshift=True,
        freq_title="Frequency specturm of the Shannon Energy Envelope",
        time_title="Time specturm of the Shannon Energy Envelope"
    )
    
    timeFrequencyPlot(
        processor.see_normalized, 
        processor.Fs_target, 
        ax[1][0], 
        ax[1][1], 
        apply_fftshift=True,
    )
    ax[0][0].sharex(ax[1][0])
    ax[0][1].sharex(ax[1][1])
    ax[2][0].sharex(ax[1][0])
    
    
    ax[1][0].scatter(processor.s1_peaks[:,0] / processor.Fs_target, processor.see_normalized[processor.s1_peaks[:,0]], c="red", marker="^", label="S1")
    ax[1][0].scatter(processor.s2_peaks[:,0] / processor.Fs_target, processor.see_normalized[processor.s2_peaks[:,0]], c="green", marker="^", label="S2")
    ax[1][0].axhline(y=processor.segmentation_min_height, label="Cutoff")
    # if processor.s1_outliers.size > 0:
    #     ax[1][0].scatter(processor.s1_outliers[:,0] / processor.Fs_target, processor.see_normalized[processor.s1_outliers[:,0]], c="purple", marker="^", label="uncertain")
    # if processor.s2_outliers.size > 0:
    #     ax[1][0].scatter(processor.s2_outliers[:,0] / processor.Fs_target, processor.see_normalized[processor.s2_outliers[:,0]], c="purple", marker="^", label="uncertain")
    ax[1][0].legend()
    print(len(processor.peaks_dist))
    # ax[2][0].plot(np.array(list(processor.peaks_dist.keys())) / processor.Fs_target, processor.peaks_dist.values(), label="all", marker=".")
    ax[2][0].plot(processor.detected_peaks[:,0] / processor.Fs_target, processor.detected_peaks[:,1], label="all", marker=".")
    ax[2][0].plot(processor.s1_peaks[:,0] / processor.Fs_target, processor.s1_peaks[:,1], label="s1_peaks")
    ax[2][0].axhline(y=processor.y_line, label="Threshold", color="black")
    ax[2][0].plot(processor.s2_peaks[:,0] / processor.Fs_target, processor.s2_peaks[:,1], label="s2_peaks")
    # ax[2][0].scatter(processor.s1_outliers[:,0] / processor.Fs_target, processor.s1_outliers[:,1], label="s1_outliers", color="red")
    # ax[2][0].scatter(processor.s2_outliers[:,0] / processor.Fs_target, processor.s2_outliers[:,1], label="s2_outliers", color="orange")
    ax[2][0].grid()
    ax[2][0].legend()
    
    
    plt.show()

def main():
    """The main loop. Can be changed to choose whether to run assignment 4.2.2 or 4.2.3.
    """
    config = ConfigParser()
    segmentation(config)

if __name__ == "__main__":
    main()