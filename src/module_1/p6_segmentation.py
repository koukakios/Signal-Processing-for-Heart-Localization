import numpy as np
import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter
from lib.processing.Processor import Processor
from lib.processing.dataprocessing import HeartSound

PLOT_RAW = False

def segmentation(config, path = None, write_results: bool = True):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    paths = [
        ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav",
        ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_2.wav",
        ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-05_channel_3.wav",
        ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-05_channel_4.wav",
        ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-05_channel_5.wav",
        ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-05_channel_6.wav",
    ]
    if path is None:
        path = paths[1]
        #path = ".\\generated\\hearbeat model\\Advanced-48000Hz-66BPM-200 beats.wav"
    processor = Processor(path, config, postprocessing=True, write_result_processed=write_results, write_result_raw=write_results, subfolder="Generated sounds")
    
    processor.run()
    
    fig, ax = plt.subplots(3, 2, figsize=(8,6), constrained_layout=True)
    fig.suptitle(path)
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
    ax[1][0].scatter(processor.ind_s1[:,0] / processor.Fs_target, processor.see_normalized[processor.ind_s1[:,0]], c="orange", marker="v", label="S1 ind")
    ax[1][0].scatter(processor.ind_s1[:,1] / processor.Fs_target, processor.see_normalized[processor.ind_s1[:,1]], c="orange", marker="v")
    ax[1][0].scatter(processor.ind_s2[:,0] / processor.Fs_target, processor.see_normalized[processor.ind_s2[:,0]], c="darkgrey", marker="v", label="S2 ind")
    ax[1][0].scatter(processor.ind_s2[:,1] / processor.Fs_target, processor.see_normalized[processor.ind_s2[:,1]], c="darkgrey", marker="v")
    ax[1][0].axhline(y=processor.actual_segmentation_min_height, label="Cutoff")
    ax[1][0].axhline(y=processor.segmentation_threshold, label="Threshold", color="green")
    if processor.uncertain.size > 0:
        ax[1][0].scatter(processor.uncertain[:,0] / processor.Fs_target, processor.see_normalized[processor.uncertain[:,0]], c="purple", marker="^", label="discarded")
    ax[1][0].legend()
    ax[2][0].plot(processor.detected_peaks[:,0] / processor.Fs_target, processor.detected_peaks[:,1], label="all", marker=".")
    ax[2][0].plot(processor.s1_peaks[:,0] / processor.Fs_target, processor.s1_peaks[:,1], label="s1_peaks")
    ax[2][0].axhline(y=processor.y_line, label="Threshold", color="black")
    ax[2][0].plot(processor.s2_peaks[:,0] / processor.Fs_target, processor.s2_peaks[:,1], label="s2_peaks")
    if processor.uncertain.size > 0:
        ax[2][0].scatter(processor.uncertain[:,0] / processor.Fs_target, processor.uncertain[:,1], label="discarded", color="red")
    ax[2][0].grid()
    ax[2][0].legend()
    
    if PLOT_RAW:
        t = np.linspace(0, len(processor.x)/processor.Fs_target, len(processor.x))
        ax[2][1].plot(t, processor.x, label="Start signal")
        ax[2][1].plot(t, processor.segmented_s1_raw, label="segmented_s1")
        ax[2][1].plot(t, processor.segmented_s2_raw, label="segmented_s2")
    else:
        t = np.linspace(0, len(processor.segmented_s1)/processor.Fs_target, len(processor.segmented_s1))
        ax[2][1].plot(t, processor.y_normalized, label="Start signal")
        ax[2][1].plot(t, processor.segmented_s1, label="segmented_s1")
        ax[2][1].plot(t, processor.segmented_s2, label="segmented_s2")
    ax[2][1].grid()
    ax[2][1].legend()
    
    plt.show()

def main():
    """
    @author: Gerrald
    @date: 10-12-2025

    The main loop. Can be changed to choose whether to run assignment 4.2.2 or 4.2.3.
    
    """
    config = ConfigParser()
    segmentation(config)

if __name__ == "__main__":
    main()