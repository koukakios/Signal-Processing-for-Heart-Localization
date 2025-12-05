from lib.config.ConfigParser import ConfigParser
from src.module_2.generate import *
from os.path import join
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

config = ConfigParser()

valves = [
    ValveParams(7,60,10,10,-0.05,0.1,0.4,50,20.0,"M"),
    ValveParams(70,140,000,10,-20.0,0.0,0.63,150,15.0,"T"),
    ValveParams(320,40,20,10,-20.0,0.1,0.32,50,50,"A"),
    ValveParams(370,120,10,10,-40.0,0.1,0.6,30,30,"P")
]
BPM = 66
Fs = 50_000

len_g = config.LowpassFilter.Size
lf = config.LowpassFilter.LowFrequency
hf = config.LowpassFilter.HighFrequency
order=config.LowpassFilter.FilterOrder
size=config.LowpassFilter.Size
n = config.HeartSoundModel.NBeats

t_model, h_model = advanced_model(
    Fs,
    BPM,
    lf,
    hf,
    order,
    size,
    valves,
    n
) 
write(join(config.Generation.SoundsPath, f"Advanced-{Fs}Hz-{BPM}BPM-{n} beats.wav"), Fs, h_model)
plt.plot(h_model)
plt.show()