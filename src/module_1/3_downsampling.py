import matplotlib.pyplot as plt
from lib.plot.timeFrequencyPlot import *
from lib.config.ConfigParser import ConfigParser
from lib.processing.Processor import Processor

def assignment431():
    """The function that houses assignment 4.3.1.
    """
    Fs_original = 48e3
    Fs_target = 4e3
    print(f"The downsampling factor M should be {Fs_original / Fs_target:.0f}")

def assignment432(config: ConfigParser):
    """The function that houses assignment 4.3.2.

    Args:
        config (ConfigParser): The config object.
    """
    path = ".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav"
    
    processor = Processor(path, config, save_steps=True)
    
    processor.process()
    
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
        processor.y_downsampled, 
        processor.Fs_target, 
        ax[1][0], 
        ax[1][1], 
        samples_offset = -len(processor.g)/2, 
        apply_fftshift=True, 
        time_title="Time domain of processed recording", 
        freq_title="Frequency domain of processed recording"
    )
    ax[0][0].sharex(ax[1][0])
    ax[0][0].sharey(ax[1][0])
    
    plt.show()

def main():
    """The main loop. Can be changed to choose whether to run assignment 4.3.1 or 4.3.2.
    """
    config = ConfigParser()
    assignment432(config)
    
if __name__ == "__main__":
    main()