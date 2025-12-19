import numpy as np
from scipy.io.wavfile import write
from pathlib import Path
from os.path import join
from datetime import datetime

from lib.config.ConfigParser import ConfigParser
from lib.model.generate import *
from lib.os.pathUtils import ensure_path_exists

class Point:
    def __init__(self, x, y, z):
        self.X = x
        self.Y = y
        self.Z = z
    def toTuple(self):
        return (self.X, self.Y, self.Z)

class Model_3D:
    """
    @author: Gerrald
    @date: 12-12-2025
    """        
    def __init__(self, config: ConfigParser, source_locs: Point | list[Point], microphone_locs: list[Point]):
        """
        @author: Gerrald
        @date: 10-12-2025
        """        
        self.source_locs = np.array([pt.toTuple() for pt in ([source_locs] if isinstance(source_locs, Point) else source_locs)])
        self.microphone_locs = np.array([pt.toTuple() for pt in microphone_locs])
        
        self.config = config
        self.Fs = config.HeartSoundModel.Fs
        self.V_Body = config.Multichannel.V_body
        self.sounds_path = config.Generation.SoundsPath
        
    def generate(self, signals: list[np.ndarray[np.float64]] | np.ndarray[np.float64]):
        if isinstance(signals, np.ndarray):
            signals = [signals]
            
        modelled_signals = []

        for mic_loc in self.microphone_locs:
            new_mic_loc = np.tile(mic_loc,(len(self.source_locs),1)) # repeat the mic loc, to comply with the dimensions of np.linalg.norm
            
            # factor hundred to convert from cm to m
            dists_to_valves = np.linalg.norm((self.source_locs-new_mic_loc)/100, axis=1)
            
            # calc delays and gains using distances to the valves
            delays = dists_to_valves/self.V_Body
            gains = 1/dists_to_valves
            
            mic_signals = []
            max_delay = max(delays)
            for delay, gain, signal in zip(delays, gains, signals):
                mic_signals.append(gain * np.pad(signal, [round(delay*self.Fs), round(max_delay*self.Fs)-round(delay*self.Fs)]))
                
            modelled_signals.append(np.array(mic_signals).sum(axis=0))
        
        self.signals = modelled_signals
        return modelled_signals
    
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