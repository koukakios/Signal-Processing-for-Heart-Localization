import matplotlib.pyplot as plt
from matplotlib import axes
from lib.os.pathUtils import get_files_ext
from os.path import exists, join, basename
import pandas as pd
from scipy.io import wavfile
from scipy.fft import fft
import numpy as np

def plot_pcg(file: str, time_ax: axes.Axes, freq_ax: axes.Axes, title:str=None):
    """
    @author: Gerrald
    @date: 10-12-2025

    _summary_

    Args:
        file (str): The file to render
        time_ax (axes.Axes): The matplotlib ax to plot the time domain of the signal on.
        freq_ax (axes.Axes): The matplotlib ax to plot the time domain of the signal on.
        title (str, optional): The title of the plot. Defaults to None.
    
    """
    if title is None:
        title = basename(file).split("_")[0]
    Fs, x = wavfile.read(file)
    
    X = fft(x)
    
    t = np.linspace(0, len(x)/Fs, len(x))
    f = np.linspace(0, Fs, len(x))
    
    time_ax.plot(t, x)
    time_ax.set_xlabel("Time [s]")
    time_ax.set_ylabel("Amplitude")
    time_ax.set_title(title)
    
    freq_ax.plot(f, np.abs(X))
    freq_ax.set_xlabel("Frequency [Hz]")
    freq_ax.set_ylabel("Amplitude")
    freq_ax.set_title(title)
    

def main(pcg_dir: str = "./samples/chapter_2/", csv_data_file: str = None):
    """
    @author: Gerrald
    @date: 10-12-2025

    Creates plots of the signal and its frequency spectrum based on the files in pcg_dir

    Args:
        pcg_dir (str, optional): The path to the wav files. Defaults to "./samples/chapter_2/".
        csv_data_file (str, optional): The path to the metadata file. Defaults to None.

    Returns:
        int: 0 on success, -1 on failure
    
    """
    # Get all wav files from the samples directory
    pcgs = get_files_ext(".wav", pcg_dir)
    # Get csv data
    if csv_data_file is None:
        csv_files = get_files_ext(".csv", pcg_dir)
        if len(csv_files) > 1:
            print("ERROR: multiple csv datafiles. Please specify the correct one using the csv_data_file parameter.")
            return -1
        elif len(csv_files) == 1:
            csv_data_file = join(pcg_dir, csv_files[0])
        else:
            print("WARNING: no csv datafile found. Not using any info from the datafile.")
    else:
        if not exists(csv_data_file):
            print("ERROR: csv datafile not found. Please specify a correct one using the csv_data_file parameter.")
            return -1
            
    if csv_data_file is not None:
        data = pd.read_csv(csv_data_file)
    
    numRows = len(pcgs)
    if numRows == 0:
        print(f"ERROR: no wav files found at {pcg_dir}. Exiting.")
        return -1
             
    # Create matplotlib figure
    fig, axes = plt.subplots(len(pcgs), 2, figsize=(8,len(pcgs)*2.5), constrained_layout=True)
    
    # Generate plots
    for i, pcg in enumerate(pcgs):
        title = basename(pcg).split("_")[0]
        if csv_data_file is not None:
            condition = data.loc[data["Patient ID"] == int(title), "Outcome"].iloc[0]
            title = f"{title} - {condition}"
        plot_pcg(join(pcg_dir, pcg), axes[i][0], axes[i][1], title)

    # Show it
    plt.show()
    return 0

if __name__ == "__main__":
    main()