import numpy as np
import matplotlib.pyplot as plt

from lib.model.Model_3D import Model_3D, Point
from lib.general.generalUtils import white_noise
from lib.config.ConfigParser import ConfigParser
from lib.model.Model import Model


def apply_heart_model():
    config = ConfigParser()
    Fs = config.HeartSoundModel.Fs
    
    model = Model(config, randomize_enabled=True, simulate_S2=True)
    model.import_csv(".\\src\\module_2\\model_params.csv")
    model.set_n(2)
    mic_locs = [Point(2.5, 5, 0), # 0
                Point(2.5, 10, 0), # 1
                Point(2.5, 15, 0), # 2
                Point(7.5, 5, 0), # 3
                Point(7.5, 10, 0), # 4
                Point(7.5, 15, 0)]
    source_locs = [Point(-1,8,-15),#Order: MTAP
                  Point(3,12,-15),
                  Point(6,14,-15),
                  Point(7,9,-15)]
    signals = []
    for valve, source in zip (model.valves_init, source_locs):
        model.valves = [valve]
        t_model, heart_sound = model.generate_model()
        signals.append(heart_sound)
    
    model = Model_3D(config, source_locs, mic_locs)
    
    h = model.generate(signals)
    
    return h
    

if __name__ == "__main__":
    h = apply_heart_model()
    for i, x in enumerate(h):
        plt.plot(x, label=f"Mic {i}")
    plt.legend()
    plt.show()