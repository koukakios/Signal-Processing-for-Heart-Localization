from scipy.signal import TransferFunction, impulse, zpk2tf
import numpy as np
from src.module_2.generate import *
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter, apply_filter

class ValveParams:
    def __init__(self, duration_ms: float, freq: float, ampl:float, delay_ms:float, onset_ms:float, name: str=None):
        self.duration = duration_ms / 1000
        self.freq = freq
        self.ampl = ampl
        self.delay = delay_ms / 1000
        self.onset = onset_ms / 1000
        self.name = name
    def toStr(self):
        return [
            f"Name: {self.name}",
            f"  Duration: {self.duration*1000}ms",
            f"  Frequency: {self.freq}Hz",
            f"  Amplitude: {self.ampl}",
            f"  Delay: {self.delay*1000}ms",
            f"  Onset: {self.onset*1000}ms",
        ]

def advanced_model_valve_params(params: ValveParams, Fs:int):
    return advanced_model_valve(params.duration, params.freq, params.ampl, params.delay, params.onset, Fs)

def advanced_model_valve(duration: float, freq:float, ampl:float, delay:float, onset:float, Fs:int):
    a = 10
    onset_ampl = 0.1
    omega = 2*np.pi*freq
    
    # Create the transfer function system of the sound
    b, a = zpk2tf([], [a-1j*omega, a+1j*omega], omega)
    system = TransferFunction(b, a)
    if onset > 0:
        # Time array (from 0 to duration with step size of 1/Fs)
        t = np.linspace(0, onset, int(Fs * onset))
        # Impulse response (time domain)
        t_onset, h_onset = impulse(system, T=t)
    
    a = 1/duration
    omega = 2*np.pi*freq
    # Create the transfer function system of the sound
    b, a = zpk2tf([], [-a-1j*omega, -a+1j*omega], omega)
    system = TransferFunction(b, a)
    # Time array (from 0 to duration with step size of 1/Fs)
    t = np.linspace(0, duration, int(Fs * duration))
    # Impulse response (time domain)
    t_beat, h_beat = impulse(system, T=t)
    
    
    # Assemble reponse
    samples_delay = int(Fs * delay)
    h_out = ampl*np.concatenate([np.zeros(samples_delay), ([] if onset <= 0 else onset_ampl*h_onset), h_beat])
    t_out = np.linspace(0, delay+duration+onset, len(h_out))
    
    return t_out, h_out

def advanced_model(Fs, BPM, lf, hf, order, size, valves):
    # Generate sounds of single valves

    t_out = []
    h_out = []
    for valve in valves:
        t, h = advanced_model_valve_params(valve, Fs)
        t_out.append(t)
        h_out.append(h)
    
    # Add single valves
    h_len = int(60/BPM*Fs)
    t_total = np.linspace(0, 60/BPM, h_len)
    h_total = np.zeros(h_len)
    for h in h_out:
        if len(h) <= h_len:
            h = np.pad(h, (0, h_len - len(h)))
            h_total += h
        else:
            raise RuntimeError("One beat longer than reserved space")
    
    # Filter signal for nice thigns
    g = construct_bandpass_filter(
        lf,
        hf,
        Fs,
        order,
        size
    )
    h_filtered = apply_filter(h_total, g)
    t_filtered = np.linspace(-len(g)/Fs, (len(h_filtered) + len(g))/Fs, len(h_filtered))
    
    return t_filtered, h_filtered