from scipy.signal import TransferFunction, impulse, zpk2tf
import numpy as np
import matplotlib.pyplot as plt
from lib.config.ConfigParser import ConfigParser
import sounddevice as sd
from lib.processing.Processor import Processor
from lib.processing.functions import construct_bandpass_filter, apply_filter
from os.path import join
from scipy.io.wavfile import write
from lib.model.generate import *


def main():
    config = ConfigParser()
    Fs = config.HeartSoundModel.Fs
    BPM = config.HeartSoundModel.BPM
    n = config.HeartSoundModel.NBeats
    len_g = config.LowpassFilter.Size
    
    t_model, h_model = advanced_model(config) 
    
    h_full = np.tile(h_model, n)
    t_full = np.linspace(0, len(h_full)/Fs, len(h_full))
    write(join(config.Generation.SoundsPath, f"Advanced-{Fs}Hz-{BPM}BPM-{n} beats.wav"), Fs, h_full)
    # sd.play(h_full, Fs)
    
    plt.plot(t_full, h_full, label="Model")
    plt.title("Advanced")
    plt.legend()
    plt.grid()
    plt.show()
    
def plotOriginal():
    config = ConfigParser()
    Fs = config.HeartSoundModel.Fs
    BPM = config.HeartSoundModel.BPM
    n = config.HeartSoundModel.NBeats
    len_g = config.LowpassFilter.Size
    
    # Get original heart sound
    processor = Processor("samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav", config, save_steps=True, write_result_processed=False, write_result_raw=False)
    processor.process()
    
    shift = -2.25
    t_model, h_model = advanced_model(config) 
    
    t_original = np.linspace(shift, shift+len(processor.y_normalized)/processor.Fs_target, len(processor.y_normalized))
    # sd.play(h_full, Fs)
    
    plt.plot(t_model, h_model, label="Model")
    plt.plot(t_original, processor.y_normalized, label="Real data")
    plt.xlim(min(t_model)-0.1, max(t_model)+0.1)
    plt.title("Advanced")
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    plotOriginal()
