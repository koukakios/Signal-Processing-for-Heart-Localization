import numpy as np
from matplotlib.image import AxesImage
from matplotlib import axes
from scipy.signal import ShortTimeFFT, spectrogram
from scipy.signal.windows import gaussian

def spectogramPlot(x: list|np.ndarray, Fs: int, plot: axes.Axes, title:str=None):
    """
    @author: Gerrald
    @date: 10-12-2025

    Plots a spectogram

    Args:
        x (list | np.ndarray): The input signal.
        Fs (int): The sampling frequency.
        plot (axes.Axes): The matplotlib axes object to plot the image on.
        title (str, optional): The title of the plot. Defaults to None.
    
    """

    N = len(x)
    win = ('gaussian', 1e-2 * Fs) # Gaussian with 0.01 s standard dev.
    SFT = ShortTimeFFT.from_window(win, Fs, nperseg=256, noverlap=125,
        fft_mode='centered', scale_to='psd', phase_shift=None)
    Sx2 = SFT.spectrogram(x)
    t_lo, t_hi = SFT.extent(N)[:2] # time range of plot
    t = np.linspace(t_lo, t_hi, len(x))
    f = np.linspace(-Fs/2, Fs/2, len(Sx2))

    
    Sx_dB = 10 * np.log10(np.fmax(Sx2, 1e-4))
    plot.imshow(Sx_dB, origin='lower', aspect='auto', extent=SFT.extent(N))
    plot.set_ylim(0, Fs/2)
    plot.set_xlabel("Time [s]")
    plot.set_ylabel("Frequency [Hz]")
    plot.set_title(title)
    
    