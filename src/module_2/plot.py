import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from copy import deepcopy
import sounddevice as sd
from copy import deepcopy
from pathlib import Path
from math import ceil
from lib.config.ConfigParser import ConfigParser
from lib.processing.Processor import Processor
from src.module_2.generate import *
from scipy.fft import fft, fftshift

mpl.use('qtagg')
mpl.rcParams["path.simplify"] = True
mpl.rcParams["path.simplify_threshold"] = 1
mpl.rcParams['figure.raise_window'] = False
plt.ion()

class Plot:
    def __init__(self, soundfile: str, config: ConfigParser, log_enabled: bool = True):
        sound_path = Path(soundfile)
        if not sound_path.exists():
            raise IOError(f"{sound_path.resolve()} does not exist")
        
        self.sound_path = sound_path
        self.log_enabled = log_enabled
        
        self.config = config
        self.Fs = config.HeartSoundModel.Fs
        self.len_g = config.LowpassFilter.Size
        self.lf = config.LowpassFilter.LowFrequency
        self.hf = config.LowpassFilter.HighFrequency
        self.order=config.LowpassFilter.FilterOrder
        self.size=config.LowpassFilter.Size
        
        self.n = self.n_init = config.HeartSoundModel.NBeats
        self.BPM = self.BPM_init = config.HeartSoundModel.BPM
        self.shift = self.shift_init = -2.28
        self.valves_init = [
            ValveParams( 10, 30, 10, 10, 0.05, 0.1,   1,  50,  50, "M"), 
            ValveParams( 40, 30, 10, 10, 0.05, 0.1, 0.5, 150, 150, "T"), 
            ValveParams(300, 30, 10, 10, 0.05, 0.1, 0.5,  50,  50, "A"), 
            ValveParams(330, 30, 10, 10, 0.05, 0.1, 0.4,  30,  30, "P"), 
        ]
        self.valves = deepcopy(self.valves_init)
        
        self.original_length = None
        self.orignal_Fs = None
        self.fig = None
        self.original = None
        self.model = None
        
    def plot_init(self):
        original_y, original_freq, original_Y = self.get_original_data()
        t_model, h_model, freq, H = self.get_model()
        min_t = min(t_model)-0.1
        max_t = max(t_model)+0.1
        
        self.fig, ax = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)    
        
        timeax = ax[0]
        freqax = ax[1]
        
        self.model, = timeax.plot(t_model, h_model, label="Model")
        self.original, = timeax.plot(self.get_original_time(), original_y, label="Real data")
        
        timeax.set_xlim(min_t, max_t)
        timeax.set_title("Match model with real data in time domain")
        timeax.legend(loc="best")
        timeax.grid(True)
        timeax.set_xlabel("Time [s]")
        timeax.set_ylabel("Amplitude")
        
        self.model_freq, = freqax.plot(freq, np.abs(H), label="Model")
        freqax.plot(original_freq, np.abs(original_Y), label="Real data")
        
        freqax.set_xlim(0, np.max(original_freq))
        freqax.set_title("Match model with real data in frequency domain")
        freqax.legend(loc="best")
        freqax.grid(True)
        freqax.set_xlabel("Freq [Hz]")
        freqax.set_ylabel("Amplitude")
        
    def update_original(self, refresh_view: bool = True):
        t = self.get_original_time()
        self.original.set_xdata(t)
                
        if refresh_view:
            self.fig.canvas.draw_idle()
            
        
    def update_model(self, refresh_view: bool = True):
        t, h, freq, H = self.get_model()
        
        self.model.set_xdata(t)
        self.model.set_ydata(h)
        self.model_freq.set_xdata(freq)
        self.model_freq.set_ydata(np.abs(H))
        
        if refresh_view:
            self.fig.canvas.draw_idle()
            
        
    def get_original_data(self):
        processor = Processor(self.sound_path.resolve(), self.config, save_steps=True, write_result_processed=False, write_result_raw=False)
        processor.process()
        
        self.original_length = len(processor.y_normalized)
        self.original_Fs = processor.Fs_target
        
        Y = fftshift(fft(processor.y_normalized))
        Y = Y/np.max(np.abs(Y))
        freq = np.linspace(-processor.Fs_target/2, processor.Fs_target/2, len(Y))
        
        return processor.y_normalized, freq, Y
        
    def get_original_time(self):
        return np.linspace(self.shift, self.shift+self.original_length/self.original_Fs, self.original_length)
        
    def get_model(self):
        t_model, h_model = advanced_model(
            self.Fs,
            self.BPM,
            self.lf,
            self.hf,
            self.order,
            self.size,
            self.valves,
            self.n
        ) 
        
        H = fftshift(fft(h_model))
        H = H/np.max(np.abs(H))
        freq = np.linspace(-self.Fs/2, self.Fs/2, len(H))
        
        return t_model, h_model, freq, H
    
    def reset(self):
        self.n = self.n_init
        self.BPM = self.BPM_init
        self.shift = self.shift_init
        self.valves = deepcopy(self.valves_init)
        
        self.update_model(refresh_view=False)
        self.update_original()
        
    def generate_summary(self):
        s = ""
        s += f"""File: {self.sound_path.stem}\n Original:\n  - shift: {self.shift}s\n Model:\n  - BPM: {self.BPM}\n  - n: {self.n}\n  - Valves:\n"""
        for valve in self.valves:
            s += ("      - " + "\n        ".join(valve.toStr())+"\n")
        return s
            
    def export_text(self, file):
        file = Path(file)
        file.parent.mkdir(parents=True, exist_ok=True)
        with open(file, "w") as fp:
            fp.write(self.generate_summary())
            
    def export_csv(self, file):
        file = Path(file)
        file.parent.mkdir(parents=True, exist_ok=True)
        
        contents = [[self.n,self.BPM,self.shift], self.valves[0].properties()]
        for valve in self.valves:
            contents.append(valve.values())
        
        s = "\n".join([",".join(c) for c in contents])
        
        with open(file, "w") as fp:
            fp.write(s)
        
    def print(self):
        print(self.generate_summary().strip())
            
    def play_audio(self, duration: str = ""):
        t_model, h_model = advanced_model(
            self.Fs,
            self.BPM,
            self.lf,
            self.hf,
            self.order,
            self.size,
            self.valves,
            self.n
        ) 
        if len(duration) > 0:
            try:
                duration = float(duration)
            except (ValueError, TypeError):
                print("Duration should be a float")
                return
            generated_duration = len(h_model) / self.Fs 
            if generated_duration < duration:
                h_model = np.tile(h_model, ceil(duration/generated_duration))
            sd.play(h_model[:ceil(duration*self.Fs)], self.Fs)
        else:
            sd.play(h_model, self.Fs)
        
    def stop_audio(self):
        sd.stop()
    
    def add_valve(self, name):
        self.valves.append(ValveParams( 10, 0, 0, 1, 1, 1, 1, 50, 50, name))
    
    def print_order(self):
        print("Order: M, T, A, P")
    
    def log(self, msg):
        if self.log_enabled:
            print(msg)
            
    def show(self):
        plt.show()
        
    def close(self):
        plt.close(self.fig)
        