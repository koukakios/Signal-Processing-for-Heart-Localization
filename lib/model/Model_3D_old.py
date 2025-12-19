import numpy as np
from copy import deepcopy
from scipy.io.wavfile import write
from pathlib import Path
from os.path import join
from datetime import datetime

from lib.config.ConfigParser import ConfigParser
from lib.model.Model import Model
from lib.model.generate import *
from lib.os.pathUtils import ensure_path_exists

class Model_3D:
    """
    @author: Gerrald
    @date: 12-12-2025
    """        
    def __init__(self, config: ConfigParser, reduce_n: bool = True, simulate_S1: bool = True, simulate_S2: bool = True, log_enabled: bool = False):
        """
        @author: Gerrald
        @date: 10-12-2025
        """        
        self.valve_locs = {
            "M":(6.37,10.65,6.00), # M
            "T":(0.94,9.57,5.5), # T
            "A":(5.5,11.00,3.6), # A
            "P":(3.9,11.5,4.5)# P
        } 

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
        self.sounds_path = config.Generation.SoundsPath
        self.V_Body = config.Multichannel.V_body
        self.simulate_S1 = simulate_S1
        self.simulate_S2 = simulate_S2
        self.model = Model(self.config)
        self.signals = None
        self.valves = None
        
    def import_csv(self, file_path: str|Path):
        """
        @author: Gerrald
        @date: 12-12-2025
        """     
        if not Path(file_path).exists():
            raise IOError(f"{file_path} cannot be found")
        
        self.model.import_csv(file_path)
        if self.reduce_n:
            self.model.set_n(10)
        else:
            self.model.set_n(self.config.HeartSoundModel.NBeats)
        
        self.valves = self.model.valves
        
    def generate(self):
        """
        @author: Gerrald
        @date: 12-12-2025
        """        
        valve_params = deepcopy(self.valves)
        valve_locs = deepcopy(self.valve_locs)
        
        incl_valves = []
        if self.simulate_S1: incl_valves.extend(["M", "T"])
        if self.simulate_S2: incl_valves.extend(["A", "P"])
        
        valve_params = [valve for valve in valve_params if valve.name in incl_valves]
        valve_locs = np.array([valve for key, valve in self.valve_locs.items() if key in incl_valves])
        
        valves_init = np.array([valve.num_values() for valve in valve_params])
        
        signals = []
        
        for mic_loc in self.mic_locs:
            valves = deepcopy(valves_init)
            new_mic_loc = np.tile(mic_loc,(len(valve_locs),1)) # repeat the mic loc, to comply with the dimensions of np.linalg.norm
            
            # factor hundred to convert from cm to m
            dists_to_valves = np.linalg.norm((valve_locs-new_mic_loc)/100, axis=1)
            
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
            
            self.model.valves = valvesParams
            
            _, signal = self.model.generate_model()
            
            signals.append(signal)
            
        self.signals = signals
            
        return signals, self.Fs
    
    def save(self, sub_folder: str|Path):
        """
        @author: Gerrald
        @date: 12-12-2025
        """ 
        base_folder = join(self.sounds_path, "3d-model", sub_folder)
        ensure_path_exists(base_folder, is_parent=True)
        
        if self.signals is None:
            self.generate()
            
        for i, signal in enumerate(self.signals):
            path = join(base_folder, f"generated_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_channel_{i}.wav")
            write(path, self.Fs, signal)