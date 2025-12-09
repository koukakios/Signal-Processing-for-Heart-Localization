import numpy as np
from lib.config.ConfigParser import ConfigParser
from copy import deepcopy
from lib.model.Model import Model
import matplotlib.pyplot as plt
from lib.model.generate import *


# valve_locs = {"M":np.array((6.37,10.65,6.00)),
#               "T":np.array((0.94,9.57,5.5)),
#               "A":np.array((5.5,11.00,3.6)),
#               "P":np.array((3.9,11.5,4.5))}
# mic_locs = {0: np.array((2.5, 5, 0)),
#             1: np.array((2.5, 10, 0)),
#             2: np.array((2.5, 15, 0)),
#             3: np.array((7.5, 5, 0)),
#             4: np.array((7.5, 10, 0)),
#             5: np.array((7.5, 15, 0))}

valve_locs = np.array([(6.37,10.65,6.00), # M
              (0.94,9.57,5.5), # T
              (5.5,11.00,3.6), # A
              (3.9,11.5,4.5)]) # P


mic_locs = np.array([(2.5, 5, 0), # 0
            (2.5, 10, 0), # 1
            (2.5, 15, 0), # 2
            (7.5, 5, 0), # 3
            (7.5, 10, 0), # 4
            (7.5, 15, 0)]) # 5

# for i in range(6):
#     mic_locs[i] = (2.5+(i//3)*5,(i%3)*5+5,0))



def log(msg):
    if False:
        print(msg)

def threeD_model():
    config = ConfigParser()
    
    model = Model(config)
    model.import_csv(".\\src\\module_2\\quite_good_params.csv")
    model.set_n(config.HeartSoundModel.NBeats)
    
    valves = model.valves
    
    valves_init = np.array([valve.num_values() for valve in valves])
    
    signals = []
    Fs = config.HeartSoundModel.Fs

    
    for mic_loc in mic_locs:
        valves = deepcopy(valves_init)
        log(valves)
        new_mic_loc = np.tile(mic_loc,(4,1)) # repeat the mic loc, to comply with the dimensions of np.linalg.norm
        
        dists_to_valves = np.linalg.norm(valve_locs-new_mic_loc, axis=1)
        
        # calc delays and gains using distances to the valves
        delays = dists_to_valves/config.Multichannel.V_body
        gains = 1/dists_to_valves
        # normalized the gains
        gains_normalized = gains/max(gains)
    
        log(f"{delays},{gains_normalized}")
        # Add delays
        # valves[:,0] += delays
        # Adjust for gains
        valves[:,3] *= gains_normalized
        valves[:,4] *= gains_normalized
        
        log(valves)
        
        valvesParams = [
            ValveParams(
                name="",
                delay_ms=float(valve[0])*1000,
                duration_total_ms=float(valve[1])*1000,
                duration_onset_ms=float(valve[2])*1000,
                a_onset=float(valve[3]),
                a_main=float(valve[4]),
                ampl_onset=float(valve[5]),
                ampl_main=float(valve[6]),
                freq_onset=float(valve[7]),
                freq_main=float(valve[8])
            ) for valve in valves
        ]
        
        model.valves = valvesParams
        
        _, signal = model.generate_model(randomize_enabled=True)
        
        signals.append(signal)
        
    return signals, Fs

def plot(signals, Fs):
    for i, signal in enumerate(signals):
        t = np.linspace(0, len(signal)/Fs, len(signal))
        plt.plot(t, signal, label=f"Mic {i}")
    plt.legend(loc="best")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    signals, Fs = threeD_model()
    plot(signals, Fs)