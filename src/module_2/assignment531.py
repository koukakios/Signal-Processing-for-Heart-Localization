import numpy as np
from lib.config.ConfigParser import ConfigParser
from copy import deepcopy
import matplotlib.pyplot as plt
from lib.model.generate import *
from lib.model.Model_3D_old import Model_3D

# Define what this program should do
WRITE = False
PLOT = True
S1 = False
S2 = True

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
    model = Model_3D(config, reduce_n=True, simulate_S1=S1, simulate_S2=S2)
    model.model.randomize_enabled = True
    model.import_csv(".\\src\\module_2\\model_params.csv")
    signals, Fs = model.generate()
    if PLOT:
        plot(signals, Fs)
    if WRITE:
        model.generate()
        name = "S1+S2" if S1 and S2 else "S1" if S1 else "S2" if S2 else "None"
        model.save(name)