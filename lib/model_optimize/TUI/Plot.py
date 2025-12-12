import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import sounddevice as sd
from pathlib import Path
from math import ceil

from lib.config.ConfigParser import ConfigParser
from lib.model.Model import Model
from lib.model.OriginalSound import OriginalSound
from lib.os.pathUtils import *
from lib.model.generate import *

mpl.use('qtagg')
mpl.rcParams["path.simplify"] = True
mpl.rcParams["path.simplify_threshold"] = 1
mpl.rcParams['figure.raise_window'] = False
plt.ion()

class Plot:
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    def __init__(self, soundfile: str, config: ConfigParser, log_enabled: bool = True):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        self.log_enabled = log_enabled
        
        self.model = Model(config)
        self.original_sound = OriginalSound(soundfile, config)
        self.Fs = config.HeartSoundModel.Fs
        
        self.original_length = None
        self.orignal_Fs = None
        self.fig = None
        self.original_plot = None
        self.model_plot = None
        
    def plot_init(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        original_y, original_freq, original_Y = self.original_sound.get_sound_init()
        t_model, h_model, freq, H = self.model.generate_model_and_freq()
        min_t = min(t_model)-0.1
        max_t = max(t_model)+0.1
        
        self.fig, ax = plt.subplots(1, 2, figsize=(8,4), constrained_layout=True)    
        
        timeax = ax[0]
        freqax = ax[1]
        
        self.model_plot, = timeax.plot(t_model, h_model, label="Model")
        self.original_plot, = timeax.plot(self.original_sound.get_time(), original_y, label="Real data")
        
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
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        t = self.original_sound.get_time()
        self.original_plot.set_xdata(t)
                
        if refresh_view:
            self.fig.canvas.draw_idle()
            
        
    def update_model(self, refresh_view: bool = True):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        t, h, freq, H = self.model.generate_model_and_freq()
        
        self.model_plot.set_xdata(t)
        self.model_plot.set_ydata(h)
        self.model_freq.set_xdata(freq)
        self.model_freq.set_ydata(np.abs(H))
        
        if refresh_view:
            self.fig.canvas.draw_idle()
    
    def reset(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        self.model.reset()
        self.original_sound.reset()
        
        self.update_model(refresh_view=False)
        self.update_original()
        
    def generate_summary(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        return self.original_sound.generate_summary() + "\n" + self.model.generate_summary()
            
    def export_readable(self, file_path):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        ensure_path_exists(file_path)
        with open(file_path, "w") as fp:
            fp.write(self.generate_summary())
            
    def export_csv(self, file_path: str):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        ensure_path_exists(file_path)
        
        contents = self.original_sound.generate_csv() + "\n" + self.model.generate_csv()
        
        with open(file_path, "w") as fp:
            fp.write(contents)
            
    def import_csv(self, file: str):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        file = Path(file)
        if not file.exists():
            print(f"{file} can not be found")
            return
        
        with open(file) as fp:
            contents = fp.read()
        
        self.model.import_csv_s(contents)        
        self.original_sound.import_csv_s(contents)

        self.update_model(refresh_view=False)
        self.update_original()
        
    def print(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        print(self.generate_summary().strip())
            
    def play_audio(self, duration: str = ""):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        t_model, h_model = self.model.generate_model()
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
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        sd.stop()
    
    def print_order(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        print("Order: M, T, A, P")
    
    def log(self, msg):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if self.log_enabled:
            print(msg)
            
    def show(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        plt.show()
        
    def close(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        plt.close(self.fig)
        