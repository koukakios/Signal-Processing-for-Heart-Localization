from lib.model.Model_3D import Model_3D, Point
from lib.general.generalUtils import white_noise
from lib.config.ConfigParser import ConfigParser
import numpy as np
import matplotlib.pyplot as plt

SIGNAL_LENGTH = 0.25

def main():
    config = ConfigParser()
    Fs = config.HeartSoundModel.Fs
    
    signal = white_noise(SIGNAL_LENGTH, Fs)
    mic_locs = [Point(2.5, 5, 0), # 0
                Point(2.5, 10, 0), # 1
                Point(2.5, 15, 0), # 2
                Point(7.5, 5, 0), # 3
                Point(7.5, 10, 0), # 4
                Point(7.5, 15, 0)]
    source_loc = Point(-1,8,-15)
    
    model = Model_3D(config, source_loc, mic_locs)
    
    h = model.generate(signal)
    
    for i, x in enumerate(h):
        plt.plot(x, label=f"Mic {i}")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()