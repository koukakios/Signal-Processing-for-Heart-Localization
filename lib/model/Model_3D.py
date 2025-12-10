import numpy as np
from lib.config.ConfigParser import ConfigParser
from copy import deepcopy
from lib.model.Model import Model
import matplotlib.pyplot as plt
from lib.model.generate import *

class Model_3D:
    """
    @author: Gerrald
    @date: 10-12-2025
    """        
    def __init__(self, config: ConfigParser, reduce_n: bool = True, log_enabled: bool = False):
        """
        @author: Gerrald
        @date: 10-12-2025
        """        
        self.valve_locs = np.array([(6.37,10.65,6.00), # M
              (0.94,9.57,5.5), # T
              (5.5,11.00,3.6), # A
              (3.9,11.5,4.5)]) # P

        self.mic_locs = np.array([(2.5, 5, 0), # 0
                    (2.5, 10, 0), # 1
                    (2.5, 15, 0), # 2
                    (7.5, 5, 0), # 3
                    (7.5, 10, 0), # 4
                    (7.5, 15, 0)]) # 5
        
        self.config = config
        self.reduce_n = reduce_n
        self.log_enabled = log_enabled
        self.Fs = config.HeartSoundModel.Fs
        self.V_Body = config.Multichannel.V_body
        
    def generate(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """        
        model = Model(self.config)
        model.import_csv(".\\src\\module_2\\model_params.csv")
        if self.reduce_n:
            model.set_n(10)
        
        valves = model.valves
        
        valves_init = np.array([valve.num_values() for valve in valves])
        
        signals = []

        
        for mic_loc in self.mic_locs:
            valves = deepcopy(valves_init)
            new_mic_loc = np.tile(mic_loc,(4,1)) # repeat the mic loc, to comply with the dimensions of np.linalg.norm
            
            dists_to_valves = np.linalg.norm(self.valve_locs-new_mic_loc, axis=1)
            
            # calc delays and gains using distances to the valves
            delays = dists_to_valves/self.V_Body
            gains = 1/dists_to_valves
            # normalized the gains
            gains_normalized = gains/max(gains)
        
            # Add delays
            valves[:,0] += delays
            # Adjust for gains
            valves[:,3] *= gains_normalized
            valves[:,4] *= gains_normalized
            
            
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
            
            _, signal = model.generate_model()
            
            signals.append(signal)
            
        return signals, self.Fs