import matplotlib.pyplot as plt
from lib.config.ConfigParser import ConfigParser
from lib.model_optimize.TUI.Plot import Plot

config = ConfigParser()
p = Plot(".\\samples\\stethoscope_2_realHeart_\\recording_2025-07-10_14-34-04_channel_2.wav", config)
p.plot_init()
p.import_csv(".\\src\\module_2\\model_params.csv")
plt.ioff()
p.show()