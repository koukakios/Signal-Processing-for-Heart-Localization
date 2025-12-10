from scipy.signal import TransferFunction, impulse, zpk2tf
from typing import Tuple
import numpy as np

from lib.model.ValveParams import ValveParams
from lib.config.ConfigParser import ConfigParser
from lib.processing.functions import construct_bandpass_filter, apply_filter
from lib.general.generalUtils import randomize


def advanced_model_valve_params(params: ValveParams, Fs:int):
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Wrapper for the advanced_model_valve function to make calls less verbose.

    Args:
        params (ValveParams): The parameters of the valve to simulate.
        Fs (int): The sampling frequency of the (virtual) microphone in Hz.

    Returns:
        Tuple[np.ndarray, np.ndarray]: t_model, h_model
    """    
    return advanced_model_valve(delay = params.delay, duration_total = params.duration_total, duration_onset = params.duration_onset, 
                                a_onset = params.a_onset, a_main = params.a_main, ampl_onset = params.ampl_onset,  
                                ampl_main = params.ampl_main, freq_onset = params.freq_onset, freq_main = params.freq_main, Fs = Fs)

def advanced_model_valve(delay:float, duration_total: float, duration_onset:float, a_onset: float, a_main: float, 
                         ampl_onset: float,  ampl_main:float, freq_onset:float, freq_main:float, Fs:int) -> Tuple[np.ndarray, np.ndarray]:
    """    
    @author: Gerrald
    @date: 10-12-2025
    
    Models a single valve for a single beat with the given parameters.

    Args:
        delay (float): The delay till the sound starts in s.
        duration_total (float): The total duration (including onset) of the sound in s.
        duration_onset (float): The duration of the onset of the sound in s.
        a_onset (float): The gain of the onset. Negative means dampened amplitude, positive exploding amplitude.
        a_main (float): The gain of the main part of the sound. Negative means dampened amplitude, positive exploding amplitude.
        ampl_onset (float): The amplitude of the onset.
        ampl_main (float): The amplitude of the main part.
        freq_onset (float): The frequency of the onset in Hz.
        freq_main (float): The frequency of the main part in Hz.
        Fs (int): The sampling frequency of the (virtual) microphone in Hz.

    Returns:
        Tuple[np.ndarray, np.ndarray]: t_model, h_model
    """    
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

def advanced_model_single_beat(Fs: int, BPM: int, lf: float, hf: float, order: int, size: int, valves: list[ValveParams]) -> Tuple[np.ndarray, np.ndarray]:
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Assemble different valve sounds to produce one single heart beat.

    Args:
        Fs (int): The sampling frequency of the (virtual) microphone in Hz.
        BPM (int): The BPM of the simulated heart
        lf (float): The lower frequency of the bandpass filter that is used to filter the heartsound in preprocessing in Hz.
        hf (float): The upper frequency of the bandpass filter that is used to filter the heartsound in preprocessing in Hz.
        order (int): The order of the bandpass filter.
        size (int): The length of the bandpass filter.
        valves (list[ValveParams]): A list of the valve parameters.

    Returns:
        Tuple[np.ndarray, np.ndarray]: t_model, h_model
    """    
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

def advanced_model(Fs: int, BPM: int, lf: float, hf: float, order: int, size: int, valves: list[ValveParams], n: int, 
                   randomize_enabled: bool = False, r_ratio: float = 0, bpm_ratio: float = 0, noise: float = 0) -> Tuple[np.ndarray, np.ndarray]:
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Assemble different valve sounds to produce n heart beats.

    Args:
        Fs (int): The sampling frequency of the (virtual) microphone in Hz.
        BPM (int): The BPM of the simulated heart
        lf (float): The lower frequency of the bandpass filter that is used to filter the heartsound in preprocessing in Hz.
        hf (float): The upper frequency of the bandpass filter that is used to filter the heartsound in preprocessing in Hz.
        order (int): The order of the bandpass filter.
        size (int): The length of the bandpass filter.
        valves (list[ValveParams]): A list of the valve parameters.
        n (int): The amount of beats.
        randomize_enabled (bool, optional): Whether to randomize the parameters a bit. Defaults to False.
        r_ratio (float, optional): How much to randomize each valve parameter. Defaults to 0.
        bpm_ratio (float, optional): How much to randomize the BPM. Defaults to 0.
        noise (float, optional): How much noise there is. Defaults to 0.

    Returns:
        Tuple[np.ndarray, np.ndarray]: t_model, h_model
    """
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
        


def repeat(n: int, h_filtered: np.ndarray, t_filtered: np.ndarray, Fs: int, length: int) -> Tuple[np.ndarray, np.ndarray]:
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Repeat h_filtered n times with a length of length for each h_filtered.

    Args:
        n (int): The amount of times to repeat h_filtered.
        h_filtered (np.ndarray): The amplitude axis of the model.
        t_filtered (np.ndarray): The time axis of the model.
        Fs (int): The sampling frequency in Hz.
        length (int): How much space each h_filtered should take up.

    Returns:
        Tuple[np.ndarray, np.ndarray]: t_model, h_model
    """    
    h_full = np.zeros(length * n + max(0, len(h_filtered) - length))
    for i in range(0, n * length, length):
        h_full[i:i+len(h_filtered)] += h_filtered
    t_full = np.linspace(0, len(h_full)/Fs, len(h_full))
    
    return t_full, h_full