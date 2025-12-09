from scipy.signal import TransferFunction, impulse, zpk2tf
import numpy as np
from lib.model.generate import *
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter, apply_filter
from random import random

class ValveParams:
    def __init__(self, delay_ms:float, duration_total_ms: float, duration_onset_ms:float, a_onset: float, a_main: float, 
                         ampl_onset: float,  ampl_main:float, freq_onset:float, freq_main:float, name: str=None):
        self.delay = delay_ms / 1000
        self.duration_total = duration_total_ms / 1000
        self.duration_onset = duration_onset_ms / 1000
        self.a_onset = a_onset
        self.a_main = a_main
        self.ampl_onset = ampl_onset
        self.ampl_main = ampl_main
        self.freq_onset = freq_onset
        self.freq_main = freq_main

        self.name = name
    def toStr(self):
        return [
            f"Name: {self.name}",
            f"  Delay: {self.delay*1000}ms",
            f"  Total duration: {self.duration_total*1000}ms",
            f"  Duration onset: {self.duration_onset*1000}ms",
            f"  A onset: {self.a_onset}",
            f"  A main: {self.a_main}",
            f"  Ampl onset: {self.ampl_onset}",
            f"  Ampl main: {self.ampl_main}",
            f"  Freq onset: {self.freq_onset}Hz",
            f"  Freq main: {self.freq_main}Hz",
        ]
    def properties(self):
        return "name,delay,duration_total,duration_onset,a_onset,a_main,ampl_onset,ampl_main,freq_onset,freq_main"
    def values_str(self):
        return list(map(str, [self.name,self.delay,self.duration_total,self.duration_onset,self.a_onset,self.a_main,self.ampl_onset,self.ampl_main,self.freq_onset,self.freq_main]))
    def num_values(self):
        return [self.delay,self.duration_total,self.duration_onset,self.a_onset,self.a_main,self.ampl_onset,self.ampl_main,self.freq_onset,self.freq_main]
    def randomize(self, ratio):
        self.delay = randomize(self.delay, ratio)
        self.duration_total = randomize(self.duration_total, ratio)
        self.duration_onset = randomize(self.duration_onset, ratio)
        self.a_onset = randomize(self.a_onset, ratio)
        self.a_main = randomize(self.a_main, ratio)
        self.ampl_onset = randomize(self.ampl_onset, ratio)
        self.ampl_main = randomize(self.ampl_main, ratio)
        self.freq_onset = randomize(self.freq_onset, ratio)
        self.freq_main = randomize(self.freq_main, ratio)

def advanced_model_valve_params(params: ValveParams, Fs:int):
    return advanced_model_valve(delay = params.delay, duration_total = params.duration_total, duration_onset = params.duration_onset, 
                                a_onset = params.a_onset, a_main = params.a_main, ampl_onset = params.ampl_onset,  
                                ampl_main = params.ampl_main, freq_onset = params.freq_onset, freq_main = params.freq_main, Fs = Fs)

def advanced_model_valve(delay:float, duration_total: float, duration_onset:float, a_onset: float, a_main: float, 
                         ampl_onset: float,  ampl_main:float, freq_onset:float, freq_main:float, Fs:int):
    # a_onset = 10
    # ampl_onset = 0.1
    # freq_onset = freq_main
    duration_main = duration_total - duration_onset if duration_total >= duration_onset else 0
    
    if duration_onset > 0:
        omega_onset = 2*np.pi*freq_onset
    
        # Create the transfer function system of the sound
        b, a = zpk2tf([], [a_onset-1j*omega_onset, a_onset+1j*omega_onset], omega_onset)
        system = TransferFunction(b, a)
        # Time array (from 0 to duration with step size of 1/Fs)
        t = np.linspace(0, duration_onset, int(Fs * duration_onset))
        # Impulse response (time domain)
        t_onset, h_onset = impulse(system, T=t)
        h_onset *= ampl_onset
    
    if duration_main > 0:
        omega_main = 2*np.pi*freq_main
        # Create the transfer function system of the sound
        b, a = zpk2tf([], [a_main-1j*omega_main, a_main+1j*omega_main], omega_main)
        system = TransferFunction(b, a)
        # Time array (from 0 to duration with step size of 1/Fs)
        t = np.linspace(0, duration_main, int(Fs * duration_main))
        # Impulse response (time domain)
        t_main, h_main = impulse(system, T=t)
        h_main *= ampl_main
    
    
    # Assemble reponse
    samples_delay = int(Fs * delay)
    h_out = np.concatenate([np.zeros(samples_delay), ([] if duration_onset <= 0 else h_onset), ([] if duration_main <= 0 else h_main)])
    t_out = np.linspace(0, delay+duration_main+duration_onset, len(h_out))
    
    return t_out, h_out

def advanced_model_single_beat(Fs, BPM, lf, hf, order, size, valves):
    # Generate sounds of single valves
    t_out = []
    h_out = []
    for valve in valves:
        t, h = advanced_model_valve_params(valve, Fs)
        t_out.append(t)
        h_out.append(h)
    
    # Add single valves
    h_len = int(60/BPM*Fs) - size
    h_len_real = max([len(h) for h in h_out])
    t_total = np.linspace(0, 60/BPM, h_len)
    h_total = np.zeros(h_len_real)
    for h in h_out:
        if len(h) <= h_len_real:
            h = np.pad(h, (0, h_len_real - len(h)))
        h_total += h
        
        if len(h) > h_len:
            print("WARNING: one beat is longer than expected, check for overlap")
    
    # Filter signal for nice thigns
    g = construct_bandpass_filter(
        lf,
        hf,
        Fs,
        order,
        size
    )
    h_filtered = apply_filter(h_total, g)
    t_filtered = np.linspace(-len(g)/Fs/2, (len(h_filtered) + len(g))/Fs/2, len(h_filtered))
    
    return t_filtered, h_filtered

def advanced_model(Fs, BPM, lf, hf, order, size, valves, n, randomize_enabled: bool = False, r_ratio: float = 0, bpm_ratio: float = 0, noise: float = 0):
    if not randomize_enabled:
        t_filtered, h_filtered = advanced_model_single_beat(Fs, BPM, lf, hf, order, size, valves)
        return repeat(n, h_filtered, t_filtered, Fs, int(60/BPM*Fs))
    else:
        max_h_len = int(60/(BPM*(1-bpm_ratio))*Fs) * n
        h_full = np.random.rand(max_h_len) * noise
        current_h_index = 0
        for i in range(n):
            BPM_randomized = randomize(BPM, bpm_ratio)
            [valve.randomize(r_ratio) for valve in valves]
            
            this_h_len = int(60/BPM_randomized*Fs)
            
            t_filtered, h_filtered = advanced_model_single_beat(
                Fs, 
                BPM_randomized, 
                lf, 
                hf, 
                order, 
                size, 
                valves)
            h_full[current_h_index:current_h_index+len(h_filtered)] += h_filtered
            current_h_index += this_h_len
        t_full = np.linspace(0, len(h_full)/Fs, len(h_full))
        return t_full, h_full
        
def randomize(val, ratio):
    return val * (1 + ratio * random())

def repeat(n, h_filtered, t_filtered, Fs, length):
    h_full = np.zeros(length * n + max(0, len(h_filtered) - length))
    for i in range(0, n * length, length):
        h_full[i:i+len(h_filtered)] += h_filtered
    t_full = np.linspace(0, len(h_full)/Fs, len(h_full))
    
    return t_full, h_full
