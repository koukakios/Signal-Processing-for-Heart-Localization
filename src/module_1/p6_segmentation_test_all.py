from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import traceback
from lib.plot.timeFrequencyPlot import *
from lib.plot.frequencyUtils import getDamping
from lib.general.generalUtils import todB
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter
from lib.processing.Processor import Processor
from lib.processing.dataprocessing import HeartSound
from lib.config.ConfigParser import ConfigParser

files = list(Path("./samples/").glob("*_realHeart*/recording*.wav"))

config = ConfigParser()
PLOT_RAW = False

def segmentation_light(config, path = None, write_results: bool = True):
    """
    @author: Gerrald
    @date: 11-12-2025
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
    # path = "samples\\piezo_2_realHeart\\recording_2025-07-10_15-15-17_channel_6.wav"
    processor = Processor(path, config, postprocessing=True, write_result_processed=write_results, write_result_raw=write_results, subfolder="Generated sounds")
    
    processor.run()
    
    t = np.linspace
    
    fig, ax = plt.subplots(3, 1, figsize=(8,6), constrained_layout=True)
    fig.suptitle(path)
    timeFrequencyPlot(
        processor.y_energy, 
        processor.Fs_target, 
        ax[0], 
        None, 
        samples_offset=len(processor.see_filter)/2,
        apply_fftshift=True,
    )
    timeFrequencyPlot(
        processor.see, 
        processor.Fs_target, 
        ax[0], 
        None, 
        apply_fftshift=True,
        freq_title="Frequency specturm of the Shannon Energy Envelope",
        time_title="Time specturm of the Shannon Energy Envelope"
    )
    
    timeFrequencyPlot(
        processor.see_normalized, 
        processor.Fs_target, 
        ax[1], 
        None, 
        apply_fftshift=True,
    )
    ax[0].sharex(ax[1])
    ax[2].sharex(ax[1])
    
    
    ax[1].scatter(processor.s1_peaks[:,0] / processor.Fs_target, processor.see_normalized[processor.s1_peaks[:,0]], c="red", marker="^", label="S1")
    ax[1].scatter(processor.s2_peaks[:,0] / processor.Fs_target, processor.see_normalized[processor.s2_peaks[:,0]], c="green", marker="^", label="S2")
    ax[1].scatter(processor.ind_s1[:,0] / processor.Fs_target, processor.see_normalized[processor.ind_s1[:,0]], c="orange", marker="v", label="S1 ind")
    ax[1].scatter(processor.ind_s1[:,1] / processor.Fs_target, processor.see_normalized[processor.ind_s1[:,1]], c="orange", marker="v")
    ax[1].scatter(processor.ind_s2[:,0] / processor.Fs_target, processor.see_normalized[processor.ind_s2[:,0]], c="darkgrey", marker="v", label="S2 ind")
    ax[1].scatter(processor.ind_s2[:,1] / processor.Fs_target, processor.see_normalized[processor.ind_s2[:,1]], c="darkgrey", marker="v")
    ax[1].axhline(y=processor.actual_segmentation_min_height, label="Cutoff")
    ax[1].axhline(y=processor.segmentation_threshold, label="Threshold", color="green")
    if processor.uncertain.size > 0:
        ax[1].scatter(processor.uncertain[:,0] / processor.Fs_target, processor.see_normalized[processor.uncertain[:,0]], c="purple", marker="^", label="discarded")
    ax[1].legend(loc="upper right")
    ax[2].plot(processor.detected_peaks[:,0] / processor.Fs_target, processor.detected_peaks[:,1], label="all", marker=".")
    ax[2].plot(processor.s1_peaks[:,0] / processor.Fs_target, processor.s1_peaks[:,1], label="s1_peaks")
    ax[2].axhline(y=processor.y_line, label="Threshold", color="black")
    ax[2].plot(processor.s2_peaks[:,0] / processor.Fs_target, processor.s2_peaks[:,1], label="s2_peaks")
    if processor.uncertain.size > 0:
        ax[2].scatter(processor.uncertain[:,0] / processor.Fs_target, processor.uncertain[:,1], label="discarded", color="red")
    ax[2].grid()
    ax[2].legend(loc="upper right")
    
    plt.show()

# Some structure to skip the files till the file in the last var
last = ".\\samples\\piezo_4_realHeart\\recording_2025-07-10_15-19-01_channel_2.wav"
passed_last = False
for file in files:
    if not passed_last:
        if not Path(last) in files:
            print(f"WARNING: {last} not in {", ".join([file.parent.stem+"\\"+file.stem+file.suffix for file in files])}")
            break
        if Path(last) == file:
            passed_last = True
        print(f"Skipped {file.parent.stem}\\{file.stem+file.suffix}")
        continue
    try:
        segmentation_light(config, str(file), write_results = False)
    except Exception as e:
        print(f"ERROR: Failed {file}: {traceback.format_exc()}")