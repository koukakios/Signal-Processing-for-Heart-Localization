from scipy.signal import TransferFunction, impulse, zpk2tf
import numpy as np
import matplotlib.pyplot as plt
from lib.config.ConfigParser import ConfigParser
import sounddevice as sd
from lib.processing.Processor import Processor
from lib.processing.functions import construct_bandpass_filter, apply_filter
from os.path import join
from scipy.io.wavfile import write
from src.module_2.generate import *
import matplotlib as mpl
from matplotlib.widgets import Button, Slider, TextBox
from math import ceil, floor

mpl.use('qtagg')
mpl.rcParams["path.simplify"] = True
mpl.rcParams["path.simplify_threshold"] = 1

def getData():
    config = ConfigParser()

    t_model, h_model = advanced_model(config) 
    
    return t_model, h_model

def timeOriginal(shift, length, Fs):
    return np.linspace(shift, shift+length/Fs, length)
    
def matchParams():
    config = ConfigParser()
    Fs = config.HeartSoundModel.Fs
    BPM = config.HeartSoundModel.BPM
    n = config.HeartSoundModel.NBeats
    len_g = config.LowpassFilter.Size
    lf = config.LowpassFilter.LowFrequency
    hf = config.LowpassFilter.HighFrequency
    order=config.LowpassFilter.FilterOrder
    size=config.LowpassFilter.Size
    
    # Define params
    valves = [
        ValveParams(20,  50,   1,  10, 10, "M"),
        ValveParams(20, 150, 0.5,  40, 10, "T"),
        ValveParams(20,  50, 0.5, 300, 10, "A"),
        ValveParams(20,  30, 0.4, 330, 10, "P"),
    ]
    
    # Get original heart sound
    processor = Processor("samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_1.wav", config, save_steps=True, write_result_processed=False, write_result_raw=False)
    processor.process()
    
    init_shift = -2.28
    t_model, h_model = advanced_model(
        Fs,
        BPM,
        lf,
        hf,
        order,
        size,
        valves
    ) 
    
    fig, ax = plt.subplots()    
    min_t = min(t_model)-0.1
    max_t = max(t_model)+0.1
    modelplot, = ax.plot(t_model, h_model, label="Model")
    
    t = timeOriginal(init_shift, len(processor.y_normalized), processor.Fs_target)
    mask = (t >= min_t) & (t <= max_t)
    
    original, = ax.plot(t[mask], processor.y_normalized[mask], label="Real data")
    ax.set_xlim(min_t, max_t)
    ax.set_title("Advanced")
    ax.legend()
    ax.grid(True)
    
    fig.subplots_adjust(left=0.25, bottom=0.25)
    
    # Make a horizontal slider to control the frequency.
    axshift = fig.add_axes([0.25, 0.1, 0.65, 0.03])
    shift_slider = Slider(
        ax=axshift,
        label='Time (s)',
        valmin=-2.30,
        valmax=-2.25,
        valinit=init_shift,
    )
    
    x = beginx = 0.06
    beginy = 0.15
    width = 0.1
    height = 0.025
    horizontal_text_margin = 0.01
    
    props = [
        prop for prop in dir(valves[0])
        if not prop.startswith("_") and prop != "name"
    ]
    
    y = beginy   
    for name in props:
        fig.text(beginx - horizontal_text_margin, y, f"{name}", fontsize=14, ha='right', va='center')
        y -= height
    
    valueTextBoxes = []
    
    x += width
    for params in valves:
        valueTextBoxes.append([])
        y = beginy
        fig.text(x - 0.5 * width, y+height, f"{params.name}", fontsize=14, ha='center', va='center', )
        for prop in props:
            subax = fig.add_axes([x - width, y - 0.5*height, width, height]) # Align to center right
            valueTextBoxes[-1].append(TextBox(
                ax=subax,
                label="",
                initial=str(getattr(params, prop) * (1000 if prop in ["duration", "delay", "onset"] else 1))        
            ))
            y -= height
        x += width
        

    def updateOriginal():
        t = timeOriginal(shift_slider.val, len(processor.y_normalized), processor.Fs_target)
        mask = (t >= min_t) & (t <= max_t)
        original.set_xdata(t[mask])
        original.set_ydata(processor.y_normalized[mask])
        fig.canvas.draw_idle()
        
    def updateModel():
        v = valueTextBoxes
        valvesAdj = [
            ValveParams(v[0][2], v[0][3], v[0][0], v[0][1], v[0][4], "M"),
            ValveParams(v[1][2], v[1][3], v[1][0], v[1][1], v[1][4], "T"),
            ValveParams(v[2][2], v[2][3], v[2][0], v[2][1], v[2][4], "A"),
            ValveParams(v[3][2], v[3][3], v[3][0], v[3][1], v[3][4], "P"),
        ]
        _, h_model = advanced_model(
            Fs,
            BPM,
            lf,
            hf,
            order,
            size,
            valvesAdj
        ) 
        modelplot.set_ydata(h_model)
        fig.canvas.draw_idle()
        
        
    resetax = fig.add_axes([0.8, 0.025, 0.1, 0.04])
    buttonOriginal = Button(resetax, 'Apply original', hovercolor='0.975')
    resetax = fig.add_axes([0.65, 0.025, 0.1, 0.04])
    buttonModel = Button(resetax, 'Apply model', hovercolor='0.975')


    def applyOriginal(event):
        updateOriginal()
    buttonOriginal.on_clicked(applyOriginal)
    def applyModel(event):
        updateModel()
    buttonModel.on_clicked(applyModel)
    
    plt.show()



if __name__ == "__main__":
    matchParams()