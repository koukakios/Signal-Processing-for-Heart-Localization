import samplerate
from scipy.io import wavfile


def wavaudioread(filename, fs):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    fs_wav, y_wav = wavfile.read(filename)
    y = samplerate.resample(y_wav, fs / fs_wav, "sinc_best")
    return y
