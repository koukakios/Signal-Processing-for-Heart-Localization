from lib.processing.functions import *
from lib.processing.dataprocessing import *
from lib.config.ConfigParser import ConfigParser
from scipy.io import wavfile

class Processor:
    """Wrapper for the processing stage.
    
    This class allows to easily reuse code across the whole codebase and optionally save results for plotting them.
    """
    def __init__(self, file_path: str, config: ConfigParser, save_results: bool = False):
        """Initializes the processor.

        Args:
            file_path (str): The path to the wav file.
            config (ConfigParser): The config object.
            save_results (bool, optional): Whether to save the substeps. Defaults to False.
        """
        # Save path to wav file
        self.file_path = file_path
        
        # Retrieve config values
        self.lp_low_freq = config.LowpassFilter.LowFrequency
        self.lp_high_freq = config.LowpassFilter.HighFrequency
        self.lp_filter_order = config.LowpassFilter.FilterOrder
        self.lp_filter_size = config.LowpassFilter.Size
        self.Fs_target = config.Downsampling.FsTarget
        self.energy_filter_order = config.Energy.FilterOrder
        self.energy_cutoff_freq = config.Energy.CutoffFrequency
        self.energy_filter_size = config.Energy.Size
        self.segmentation_min_height = config.Segmentation.MinHeight
        self.segmentation_min_dist = config.Segmentation.MinDist * self.Fs_target
        
        self.save_results = save_results
        # Initialize fields that values can be saved to
        self.Fs_original = None
        self.x = None
        self.g = None
        self.y = None
        self.y_downsampled = None
        self.y_normalized = None
        self.y_energy = None
        self.see_filter = None
        self.see = None
        self.see_normalized = None
        self.peaks = None
        self.peak_properties = None
        self.peaks_dist = None
    def process(self):
        """Initialize the processing and optionally save the steps in between.
        """
        Fs_original, x = wavfile.read(self.file_path)
    
        g = construct_bandpass_filter(self.lp_low_freq, self.lp_high_freq, Fs_original, order=self.lp_filter_order, size=self.lp_filter_size)
        
        y = filter(x, g)
        
        y_downsampled = downsample(y, Fs_original, self.Fs_target)
        
        y_normalized = normalize(y_downsampled)
        
        y_energy = shannon_energy(y_normalized)
        
        see_filter =  construct_lowpass_filter(self.energy_cutoff_freq, self.Fs_target, self.energy_filter_order, self.energy_filter_size)
        
        see = filter(y_energy, see_filter)
        
        see_normalized = normalize(see, mode="stdev")
        
        peaks, peak_properties = get_peaks(see_normalized, self.segmentation_min_height, self.segmentation_min_dist)
        
        peaks_dist = get_dist_peaks_to_next(peaks)
        
        
        if self.save_results:
            self.Fs_original = Fs_original
            self.x = x
            self.g = g
            self.y = y
            self.y_downsampled = y_downsampled
            self.y_normalized = y_normalized
            self.y_energy = y_energy
            self.see_filter = see_filter
            self.see = see
            self.see_normalized = see_normalized
            self.peaks = peaks
            self.peak_properties = peak_properties
            self.peaks_dist = peaks_dist