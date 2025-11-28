from lib.processing.functions import *
from lib.processing.dataprocessing import *
from lib.config.ConfigParser import ConfigParser
from scipy.io import wavfile
from pathlib import Path
from scipy.io.wavfile import write
from os.path import join, basename, splitext

class Processor:
    """Wrapper for the processing stage.
    
    This class allows to easily reuse code across the whole codebase and optionally save results for plotting them.
    """
    def __init__(self, file_path: str, config: ConfigParser, save_results: bool = False, log: bool=True, write_result: bool = True):
        """Initializes the processor.

        Args:
            file_path (str): The path to the wav file.
            config (ConfigParser): The config object.
            save_results (bool, optional): Whether to save the substeps. Defaults to False.
            log (bool, optional): Whether to log its process in the console. Defaults to True.
        """
        if not Path(file_path).exists():
            raise IOError(f"{file_path} not found")
        
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
        self.segmentation_threshold = config.Segmentation.EnvelopeThreshold
        self.generation_path = config.Segmentation.OutputPath
        
        self.save_results = save_results
        self.write_result = write_result
        self.log_enabled = log
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
        self.s1_peaks = None
        self.s2_peaks = None
        self.s1_outliers = None
        self.s2_outliers = None
        self.y_line = None
        self.uncertain = None
        self.ind_s1 = None
        self.ind_s2 = None
        self.segmented_s1 = None
        self.segmented_s2 = None
    def process(self):
        """Initialize the processing and optionally save the steps in between.
        """
        self.log("Reading file...")
        Fs_original, x = wavfile.read(self.file_path)
    
        self.log("Constructing bandpass filter...")
        g = construct_bandpass_filter(self.lp_low_freq, self.lp_high_freq, Fs_original, order=self.lp_filter_order, size=self.lp_filter_size)
        
        self.log("Filtering input signal...")
        y = apply_filter(x, g)
        
        self.log("Downsampling signal...")
        y_downsampled = downsample(y, Fs_original, self.Fs_target)
        
        self.log("Normalizing signal...")
        y_normalized = normalize(y_downsampled)
        
        self.log("Calculating Shannon energy...")
        y_energy = shannon_energy(y_normalized)
        
        self.log("Constructing Shannon Energy Envelope Filter...")
        see_filter = construct_lowpass_filter(self.energy_cutoff_freq, self.Fs_target, self.energy_filter_order, self.energy_filter_size)
        
        self.log("Creating Shannon Energy Envelope...")
        see = apply_filter(y_energy, see_filter)
        
        self.log("Normalizing Shannon Energy Envelope...")
        see_normalized = normalize(see, mode="stdev")
        
        self.log("Getting peaks of Shannon Energy Envelope...")
        peaks, peak_properties = get_peaks(see_normalized, self.segmentation_min_height, self.segmentation_min_dist)
        
        self.log("Calculating distance between peaks...")
        peaks_dist = get_dist_peaks_to_next(peaks)
        
        self.log("Classifying peaks...")
        # s1_peaks, s2_peaks, s1_outliers, s2_outliers = self.classify_peaks(peaks)
        s1_peaks, s2_peaks, uncertain = self.classify_peaks(peaks)
        
        self.log("Segmenting them...")
        ind_s1 = detect_peak_domains(s1_peaks, see_normalized, self.segmentation_threshold)
        ind_s2 = detect_peak_domains(s2_peaks, see_normalized, self.segmentation_threshold)
        
        segmented_s1 = segment(y_normalized, ind_s1, len(see_filter))
        segmented_s2 = segment(y_normalized, ind_s2, len(see_filter))
        
        if self.write_result:
            self.log("Writing files...")
            file_name = splitext(basename(self.file_path))[0]
            write(join(self.generation_path, f"segmented-s1-{file_name}.wav"), self.Fs_target, segmented_s1)
            write(join(self.generation_path, f"segmented-s2-{file_name}.wav"), self.Fs_target, segmented_s2)

        
        self.log("Finished! :-)")
        # self.log(f"Results:\n  - S1 count: {len(s1_peaks)}\n  - S2 count: {len(s2_peaks)}\n  - S1 outliers count: {len(s1_outliers)}\n  - S2 outliers count: {len(s2_outliers)}")
        self.log(f"Results:\n  - S1 count: {len(s1_peaks)}\n  - S2 count: {len(s2_peaks)}\n  - Uncertain: {len(uncertain)}")
        
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
            self.s1_peaks = s1_peaks
            self.s2_peaks = s2_peaks
            self.uncertain = uncertain
            self.s1_outliers = None
            self.s2_outliers = None
            self.ind_s1 = ind_s1
            self.ind_s2 = ind_s2
            self.segmented_s1 = segmented_s1
            self.segmented_s2 = segmented_s2
            
    def classify_peaks(self, x_peaks: np.ndarray):
        diff = np.diff(x_peaks)
        diff2 = np.diff(diff)
        
        peaks = np.array(list(zip(x_peaks[:-2], diff[:-1], diff2)))
        
        self.detected_peaks = peaks
        
        # s2_peaks, s2_outliers, s1_peaks, s1_outliers = analyze_diff2(x_peaks, diff, diff2)
        s1_peaks, s2_peaks, uncertain = self.analyze_diff2(peaks)
        
        return s1_peaks, s2_peaks, uncertain
    
    def analyze_diff2(self, peaks):
        minima = []
        maxima = []
        uncertain = []
        prev_d = None
        # Get temporary mimima and maxima on difference plot
        for x, d, d2 in peaks:
            to_add = (x,d,d2)
            if prev_d is not None and d > prev_d and d2 < 0:
                maxima.append(to_add)
            elif prev_d is not None and d < prev_d and d2 > 0:
                minima.append(to_add)
            else:
                uncertain.append(to_add)
            prev_d = d
                
        minima = np.array(minima)
        maxima = np.array(maxima)
        
        # Sort minima descending
        minima = minima[minima[:,1].argsort()[::-1]]
        # Sort maxima ascending
        maxima = maxima[maxima[:,1].argsort()]
        
        y_line = None
        # Get line that goes through most lines in the difference plot
        while True:
            cur_min, minima = pop_np(minima)
            cur_max, maxima = pop_np(maxima)
            if cur_min[1] < cur_max[1]:
                y_line = 0.5 * (max(minima[:,1]) + min(maxima[:,1]))
            
            if y_line != None:
                break
            elif len(minima) == 0 or len(maxima) == 0:
                raise RuntimeError("No line found")
            else:
                print("Skipped some peaks, invalid line through middle")
            
        # New function: classify based on y_line
        s1 = []
        s2 = []
        uncertain = []
        prev_s1 = None
        for x, d, d2 in peaks:
            to_add = (x,d,d2)
            if d <= y_line and not prev_s1:
                s1.append(to_add)
                prev_s1 = True
            elif d > y_line and (prev_s1 or prev_s1 is None):
                s2.append(to_add)
                prev_s1 = False
            else:
                uncertain.append(to_add)
            
        if self.save_results:
            self.y_line = y_line

        return np.array(s1), np.array(s2), np.array(uncertain)
    

        
    
    def log(self, msg):
        if self.log_enabled:
            print(msg)