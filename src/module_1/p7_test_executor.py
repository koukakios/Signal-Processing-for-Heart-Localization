import matplotlib.pyplot as plt
import numpy as np

from lib.config.ConfigParser import ConfigParser
from lib.processing.Executor import Executor
from lib.plot.timeFrequencyPlot import *

def testingfunction(config):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    executor = Executor("samples\\stethoscope_2_realHeart_", config, True)
    executor.execute(write_enabled=False)
    fig, ax = plt.subplots(3, 2, sharex="all", sharey="all", constrained_layout=True)
    for file, values, plot in zip(executor.results.keys(). executor.results.values(), np.array(ax).flatten()):
        processor = values[3]
        timeFrequencyPlot(
            processor.see_normalized,
            config.Downsampling.FsTarget,
            plot,
            None,
        )
    plt.show()

def main():
    """
    @author: Gerrald
    @date: 10-12-2025

    The main loop. Can be changed to choose whether to run assignment 4.2.2 or 4.2.3.
    
    """
    config = ConfigParser()
    testingfunction(config)

if __name__ == "__main__":
    main()