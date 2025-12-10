import numpy as np
from lib.config.ConfigParser import ConfigParser
from copy import deepcopy
import matplotlib.pyplot as plt
from lib.model.generate import *
from lib.model.Model_3D import Model_3D


def plot(signals, Fs):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    for i, signal in enumerate(signals):
        t = np.linspace(0, len(signal)/Fs, len(signal))
        plt.plot(t, signal, label=f"Mic {i}")
    plt.legend(loc="best")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    config = ConfigParser()
    model = Model_3D(config, reduce_n=True)
    signals, Fs = model.generate()
    plot(signals, Fs)