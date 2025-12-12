from scipy.io import wavfile
from pathlib import Path
from scipy.io.wavfile import write
from os.path import join, basename, splitext
import matplotlib.pyplot as plt
from lib.processing.functions import *
from lib.processing.dataprocessing import *
from lib.os.pathUtils import ensure_path_exists
from lib.config.ConfigParser import ConfigParser

class Classification(Enum):
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    S1 = 0
    S2 = 1
    Uncertain = 2


class Processor:
    """
    @author: Gerrald
    @date: 11-12-2025

    Wrapper for the processing stage.
    
    This class allows to easily reuse code across the whole codebase and optionally save results for plotting them.
    
    """
    def __init__(self, file_path: str, config: ConfigParser, subfolder: str = "", log: bool=True, write_result_processed: bool = True, write_result_raw: bool = True, postprocessing: bool = True):
        """
        @author: Gerrald
        @date: 10-12-2025

        Initializes the processor.

        Args:
            file_path (str): The path to the wav file.
            config (ConfigParser): The config object.
            save_results (bool, optional): Whether to save the substeps. Defaults to False.
            log (bool, optional): Whether to log its process in the console. Defaults to True.
        
        """
        if file_path is not None and not Path(file_path).exists():
            raise IOError(f"{file_path} not found")
        
        # Save path to wav file
        self.file_path = file_path
        # Save path to folder to save results in
        self.subfolder = subfolder
        
        # Retrieve config values
        self.lp_low_freq = config.LowpassFilter.LowFrequency
        self.lp_high_freq = config.LowpassFilter.HighFrequency
        self.lp_filter_order = config.LowpassFilter.FilterOrder
        self.lp_filter_size = config.LowpassFilter.Size
        self.Fs_target = config.Downsampling.FsTarget
        self.energy_filter_order = config.Energy.FilterOrder
        self.energy_cutoff_freq = config.Energy.CutoffFrequency
        self.energy_filter_size = config.Energy.Size
        self.segmentation_solve_uncertain_length = config.Segmentation.SolveUncertainLength
        self.segmentation_min_height = config.Segmentation.MinHeight
        self.segmentation_min_dist = config.Segmentation.MinDist * self.Fs_target
        self.segmentation_threshold = config.Segmentation.EnvelopeThreshold
        self.generation_path = config.Segmentation.OutputPath
        self.concat_path = config.Segmentation.ConcatPath
        self.segmented_path = config.Segmentation.SegmentedPath
        self.max_uncertain_count_per_min = config.Segmentation.MaxUncertainCountPerMin
        self.max_comp_height = config.Segmentation.MaxCompHeight
        self.max_comp_iter = config.Segmentation.MaxCompIter
        
        self.write_result_processed = write_result_processed
        self.write_result_raw = write_result_raw
        self.log_enabled = log
        self.postprocessing = postprocessing
        # Initialize fields that values can be saved to
        self.Fs_original = None
        self.x = None
        self.g = None
        self.y = None
        self.M = None
        self.y_downsampled = None
        self.y_normalized = None
        self.y_energy = None
        self.see_filter = None
        self.see = None
        self.see_normalized = None
        self.peaks = None
        self.peak_properties = None
        self.s1_peaks = None
        self.s2_peaks = None
        self.s1_outliers = None
        self.s2_outliers = None
        self.y_line = None
        self.uncertain = None
        self.ind_s1 = None
        self.ind_s2 = None
        self.actual_segmentation_min_height = None
        self.segmented_s1 = None
        self.segmented_s2 = None
        self.segmented_s1_raw = None
        self.segmented_s2_raw = None
    def run(self):
        """
        @author: Gerrald
        @date: 10-12-2025

        Run the process.
        
        """
        self.load()
        
        self.preprocess()
        
        self.process()
    
        self.classify()

        self.segment()

        self.write()
        
        self.log("Finished! :-)")
        self.log(f"Results:\n  - S1 count: {len(self.s1_peaks)}\n  - S2 count: {len(self.s2_peaks)}\n  - Uncertain: {len(self.uncertain)}")
        
            
    def load(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if self.file_path is None:
            raise RuntimeError("Filepath is None")
        self.log("Reading file...")
        self.Fs_original, self.x = wavfile.read(self.file_path)
        
    def preprocess(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if self.x is None or self.Fs_original is None:
            self.load()
        
        self.log("Constructing bandpass filter...")
        self.g = construct_bandpass_filter(self.lp_low_freq, self.lp_high_freq, self.Fs_original, order=self.lp_filter_order, size=self.lp_filter_size)
        
        self.log("Filtering input signal...")
        self.y = apply_filter(self.x, self.g)
        
        self.log("Downsampling signal...")
        self.y_downsampled, self.M = downsample(self.y, self.Fs_original, self.Fs_target)
        
        self.log("Normalizing signal...")
        self.y_normalized = normalize(self.y_downsampled)
        
    def process(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if self.y_normalized is None:
            self.preprocess()
        self.log("Calculating Shannon energy...")
        self.y_energy = shannon_energy(self.y_normalized)
        
        self.log("Constructing Shannon Energy Envelope Filter...")
        self.see_filter = construct_lowpass_filter(self.energy_cutoff_freq, self.Fs_target, self.energy_filter_order, self.energy_filter_size)
        
        self.log("Creating Shannon Energy Envelope...")
        self.see = apply_filter(self.y_energy, self.see_filter)
        
        self.log("Normalizing Shannon Energy Envelope...")
        self.see_normalized = normalize(self.see, mode="stdev")
        
        self.log("Getting peaks of Shannon Energy Envelope...")
        self.peaks, _ = get_peaks(self.see_normalized, self.segmentation_min_height, self.segmentation_min_dist)
        
    def classify(self):
        """
        @author: Gerrald
        @date: 11-12-2025
        """
        self.log("Classifying peaks...")
        
        # Initial classification - baseline measurement
        self.s1_peaks, self.s2_peaks, self.uncertain = self.classify_peaks(self.peaks)
        
        if len(self.uncertain) > 0 and self.postprocessing:
            self.log("Postprocessing...")
            # Calculating some stats so that we can adjust the global threshold
            max_uncertain_count = self.max_uncertain_count_per_min * len(self.see_normalized) / self.Fs_target / 60
            min_height = self.segmentation_min_height
            increase = (self.max_comp_height - self.segmentation_min_height) / self.max_comp_iter
            
            if len(self.uncertain) > max_uncertain_count: self.log("Adjusting global threshold")
            
            # While we have too much uncertains (max count of uncertains per minute set in config), 
            # slowly increase the global peak threshold till we meet a value that is beneath these.
            while len(self.uncertain) > max_uncertain_count:
                min_height += increase
                
                self.peaks, _ = get_peaks(self.see_normalized, min_height, self.segmentation_min_dist)
                self.s1_peaks, self.s2_peaks, self.uncertain = self.classify_peaks(self.peaks)
                
                if min_height > self.max_comp_height:
                    t = np.linspace(0, len(self.see_normalized)/self.Fs_target, len(self.see_normalized))
                    plt.hlines(self.segmentation_min_height, xmin=0, xmax=len(self.see_normalized)/self.Fs_target, label="min")
                    plt.hlines(self.max_comp_height, xmin=0, xmax=len(self.see_normalized)/self.Fs_target, label="max")
                    plt.plot(t, self.see_normalized, color="orange", label="signal")
                    plt.title(f"Did not succeed with {Path(self.file_path).parent.stem + "/" + Path(self.file_path).stem}")
                    plt.legend()
                    plt.show()
                    # raise RuntimeError(f"Did not succeed to achieve max {max_uncertain_count} uncertains - achieved {len(self.uncertain)}")
                    self.peaks, _ = get_peaks(self.see_normalized, self.segmentation_min_height, self.segmentation_min_dist)
                    self.s1_peaks, self.s2_peaks, self.uncertain = self.classify_peaks(self.peaks)
                    print(f"Continuing with {len(self.uncertain)} uncertains")
                    break
            self.log(f"Achieved {len(self.uncertain)} uncertains")
            self.actual_segmentation_min_height = min_height
            # Do a last effort to locally increase/decrease the threshold to be more resistant against noise.
            self.s1_peaks, self.s2_peaks, self.uncertain = self.solve_uncertains(self.see_normalized, self.peaks, self.s1_peaks, self.s2_peaks, self.uncertain, 
                                                                self.segmentation_solve_uncertain_length, self.Fs_target, 
                                                                self.segmentation_min_height, self.segmentation_min_dist)
        else:
            self.actual_segmentation_min_height = 0
        

    def segment(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        self.log("Segmenting them...")
        
        # Sort arrays for further processing
        self.s1_peaks = self.s1_peaks[self.s1_peaks[:,0].argsort()]
        self.s2_peaks = self.s2_peaks[self.s2_peaks[:,0].argsort()]
        
        self.ind_s1 = detect_peak_domains(self.s1_peaks, self.see_normalized, self.segmentation_threshold)
        self.ind_s2 = detect_peak_domains(self.s2_peaks, self.see_normalized, self.segmentation_threshold)
        # Calculate compensation for filters
        see_filter_comp = int(len(self.see_filter)/2)
        g_filter_comp = int(len(self.g)/2)
        self.segmented_s1, self.segmented_s1_concat = segment(self.y_normalized, self.ind_s1, lambda index: (index - see_filter_comp))
        self.segmented_s2, self.segmented_s2_concat = segment(self.y_normalized, self.ind_s2, lambda index: (index - see_filter_comp))
        self.segmented_s1_raw, self.segmented_s1_raw_concat = segment(self.x, self.ind_s1, lambda index: (index - see_filter_comp) * self.M - g_filter_comp)
        self.segmented_s2_raw, self.segmented_s2_raw_concat = segment(self.x, self.ind_s2, lambda index: (index - see_filter_comp) * self.M - g_filter_comp)
        
    def write(self):
        # Path were it is saved "value from config/subfolder/(concat|segmented)/(raw|processed)/file"
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        basefolder = join(self.generation_path, self.subfolder)
        
        if self.write_result_processed:
            self.log("Writing processed files...")
            file_name = splitext(basename(self.file_path))[0]
            
            concat_file_path = join(basefolder, self.concat_path, "processed")
            ensure_path_exists(concat_file_path, is_parent=True)
            write(join(concat_file_path, f"segmented-s1-processed-{file_name}.wav"), self.Fs_target, self.segmented_s1_concat)
            write(join(concat_file_path, f"segmented-s2-processed-{file_name}.wav"), self.Fs_target, self.segmented_s2_concat)
            
            segment_file_path = join(basefolder, self.segmented_path, "processed")
            ensure_path_exists(segment_file_path, is_parent=True)
            write(join(segment_file_path, f"segmented-s1-processed-{file_name}.wav"), self.Fs_target, self.segmented_s1)
            write(join(segment_file_path, f"segmented-s2-processed-{file_name}.wav"), self.Fs_target, self.segmented_s2)
        if self.write_result_raw:
            self.log("Writing raw files...")
            file_name = splitext(basename(self.file_path))[0]

            concat_file_path = join(basefolder, self.concat_path, "raw")
            ensure_path_exists(concat_file_path, is_parent=True)
            write(join(concat_file_path, f"segmented-s1-raw-{file_name}.wav"), self.Fs_original, self.segmented_s1_raw_concat)
            write(join(concat_file_path, f"segmented-s2-raw-{file_name}.wav"), self.Fs_original, self.segmented_s2_raw_concat)
            
            segment_file_path = join(basefolder, self.segmented_path, "raw")
            ensure_path_exists(segment_file_path, is_parent=True)
            write(join(segment_file_path, f"segmented-s1-raw-{file_name}.wav"), self.Fs_original, self.segmented_s1_raw)
            write(join(segment_file_path, f"segmented-s2-raw-{file_name}.wav"), self.Fs_original, self.segmented_s2_raw)
            
    def classify_peaks(self, x_peaks: np.ndarray, save_y_line: bool = True, save_peaks: bool = True):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        diff = np.diff(x_peaks)
        diff2 = np.diff(diff)
        
        peaks = np.array(list(zip(x_peaks[:-2], diff[:-1], diff2)))
        
        if save_peaks:
            self.detected_peaks = peaks
        
        # s2_peaks, s2_outliers, s1_peaks, s1_outliers = analyze_diff2(x_peaks, diff, diff2)
        s1_peaks, s2_peaks, uncertain = self.analyze_diff2(peaks, save_y_line)
        
        return s1_peaks, s2_peaks, uncertain
    
    def analyze_diff2(self, peaks: np.ndarray, save_y_line: bool = True):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        minima = []
        maxima = []
        prev_d = None
        # Get temporary mimima and maxima on difference plot
        for x, d, d2 in peaks:
            to_add = (x,d,d2)
            if prev_d is not None and d > prev_d and d2 < 0:
                maxima.append(to_add)
            elif prev_d is not None and d < prev_d and d2 > 0:
                minima.append(to_add)
            prev_d = d
                
        minima = np.array(minima)
        maxima = np.array(maxima)
        
        # Sort minima ascending
        minima = minima[minima[:,1].argsort()]
        # Sort maxima descending
        maxima = maxima[maxima[:,1].argsort()[::-1]]
        
        y_line = None
        # Get line that goes through most lines in the difference plot
        while True:
            cur_min, minima = pop_np(minima)
            cur_max, maxima = pop_np(maxima)
            if cur_min[1] < cur_max[1]:
                y_line = 0.5 * (max(minima[:,1]) + min(maxima[:,1]))
            
            if y_line != None:
                #print(y_line)
                break
            elif len(minima) == 0 or len(maxima) == 0:
                raise RuntimeError("No line found")
            # else:
                #print("Skipped some peaks, invalid line through middle")
            
        # New function: classify based on y_line
        classification = []
        
        prev_s1 = None
        for x, d, d2 in peaks:
            c = Classification.Uncertain
            if d <= y_line and not prev_s1:
                c = Classification.S1
                prev_s1 = True
            elif d > y_line and (prev_s1 or prev_s1 is None):
                c = Classification.S2
                prev_s1 = False
            classification.append((x,d,d2,c))

        classification = np.array(classification)
        
        mask_uncertain = classification[:,3] == Classification.Uncertain
        mask_prev = np.concatenate(([False], mask_uncertain[:-1]))
        mask_next = np.concatenate((mask_uncertain[1:], [False]))
        
        uncertain_total_mask = mask_uncertain | mask_next # | mask_prev
        
        s1_mask = classification[:,3] == Classification.S1
        s2_mask = classification[:,3] == Classification.S2
        
        uncertain = classification[uncertain_total_mask, :3].astype(np.int64)
        s1 = classification[~uncertain_total_mask & s1_mask, :3].astype(np.int64)
        s2 = classification[~uncertain_total_mask & s2_mask, :3].astype(np.int64)
        
        if save_y_line:
            self.y_line = y_line

        return np.array(s1), np.array(s2), np.array(uncertain)
    
    def solve_uncertains(self, see: np.ndarray, peaks: np.ndarray, s1_peaks: np.ndarray, s2_peaks: np.ndarray, uncertain: np.ndarray, debug_length: float, Fs: int, min_height: float, min_dist: float):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        s1_u = []
        s2_u = []
        # Solve the uncertain thingys
        # Sort the uncertains in groups that follow each other (no peak in between)
        
        peak_to_index = {p: i for i, p in enumerate(peaks)}
        idx = np.array([peak_to_index[val] for val in uncertain[:,0]])
        breaks = np.where(np.diff(idx) > 1)[0] + 1
        # Step 3: split uncertains accordingly
        groups = np.split(uncertain, breaks)

        debug_samples = int(debug_length * Fs)
        for group in groups:
            # if (np.any(group[:,1] < self.y_line) != np.all(group[:,1] < self.y_line) or
            #         np.any(group[:,1] > self.y_line) != np.all(group[:,1] > self.y_line)):
            #     print(f"WARNING: any and all do not match {group}")
            #     # continue

            # Shortest systole is around 0.2 s ~ 800 samples
            # so if any distance between peaks is lower than 700 samples, we know for sure we have detected a peak too much
            # Or if the middle (because we padded the uncertains) is smaller than the y_lien
            if np.any(group[:,1] < 700) or group[0,1] < self.y_line:   
                success = False
                group = group[group[:,1].argsort()[::-1]]
                # Sort group height on descending distance
                group_height = np.array(list(zip(group[:,0], see[group[:,0]])))
                group_height = group_height[group_height[:,1].argsort()[::-1]]
                
                while True:
                    smallest_peak, group_height = pop_np(group_height)
                    peaks = np.setdiff1d(peaks, [smallest_peak[0]])
                    s1_peaks_new, s2_peaks_new, uncertain_new = self.classify_peaks(peaks, save_y_line = False)
                    
                    if not np.any(np.isin(uncertain_new[:,0], group_height[:,0])) and len(peaks) > 0:
                        success = True
                        break
                    elif len(group_height) == 0:
                        self.log(f"Debugging uncertains failed (going up) {group_height[:,0]}")
                        break
                if success:
                    new_s1 = get_difference(s1_peaks_new, s1_peaks)
                    new_s2 = get_difference(s2_peaks_new, s2_peaks)
                    s1_u.extend(new_s1)
                    s2_u.extend(new_s2)
            # Missed a peak, adjust threshold down
            else:
                begin_segment = group[0][0] - debug_samples
                end_segment = group[-1][0] + debug_samples
                peaks_in_segment = peaks[(peaks >= begin_segment) & (peaks <= end_segment)]
                segment = see[begin_segment:end_segment]
                success = False
                
                all_peaks, _ = signal.find_peaks(segment, distance=min_dist)
                new_peaks = np.setdiff1d(all_peaks+begin_segment, peaks_in_segment)
                if len(new_peaks) == 0:
                    self.log("Debugging uncertains failed (going down), no new peaks found.")
                    continue
                    
                new_peaks_height = see[new_peaks]
                
                while True:
                    biggest_peak_ind = np.argmax(new_peaks_height)
                    biggest_peak = new_peaks[biggest_peak_ind]
                    new_peaks_height = np.delete(new_peaks_height, biggest_peak_ind)
                    new_peaks = np.delete(new_peaks, biggest_peak_ind)
                    peaks_in_segment = np.concatenate([peaks_in_segment, [biggest_peak]])
                    # Sort peaks
                    peaks_in_segment = peaks_in_segment[peaks_in_segment.argsort()]
                    s1_peaks_new, s2_peaks_new, uncertain_new = self.classify_peaks(peaks_in_segment, save_y_line = False, save_peaks=False)
                    
                    if len(uncertain_new) == 0:
                        success = True
                        break
                    elif len(new_peaks) == 0:
                        self.log("Debugging uncertains failed (going down)")
                        break
                if success:
                    new_s1 = get_difference(s1_peaks_new, s1_peaks)
                    new_s2 = get_difference(s2_peaks_new, s2_peaks)
                    s1_u.extend(new_s1)
                    s2_u.extend(new_s2)

                    
                    
        # Get final values
        if s1_u:
            s1_peaks = np.concatenate([s1_peaks, s1_u])
        if s2_u:
            s2_peaks = np.concatenate([s2_peaks, s2_u])
        uncertain = uncertain[~(np.isin(uncertain[:,0], s1_peaks[:,0]) | np.isin(uncertain[:,0], s2_peaks[:,0]))]
        
        return s1_peaks, s2_peaks, uncertain
                
            
        
    def open_file(self, file_path):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if not Path(file_path).exists():
            raise IOError(f"{file_path} not found")
        
        # Save path to wav file
        self.file_path = file_path
        
        # Initialize fields that values can be saved to
        self.Fs_original = None
        self.x = None
        self.g = None
        self.y = None
        self.M = None
        self.y_downsampled = None
        self.y_normalized = None
        self.y_energy = None
        self.see_filter = None
        self.see = None
        self.see_normalized = None
        self.peaks = None
        self.peak_properties = None
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
        self.segmented_s1_raw = None
        self.segmented_s2_raw = None
    
    def log(self, msg):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if self.log_enabled:
            print(msg)
