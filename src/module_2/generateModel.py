import matplotlib.pyplot as plt
from lib.model.Model import Model
from lib.config.ConfigParser import ConfigParser

SAVE = False
PLOT = True

# Script that shows the usage of Model to create a model of a single microphone
config = ConfigParser()

model = Model(config, randomize_enabled=False)
model.import_csv(".\\src\\module_2\\model_params.csv")
model.set_n(config.HeartSoundModel.NBeats)
if SAVE:
    model.save()
    
if PLOT:
    t_model, h_model = model.generate_model()
    plt.rcParams.update({'font.size': 20})
    plt.plot(t_model, h_model, linewidth=2)
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (relative)")
    plt.title("Modeled heart beat signal")
    plt.grid()
    plt.show()