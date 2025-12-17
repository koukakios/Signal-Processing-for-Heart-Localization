from pathlib import Path
import numpy as np
from collections import defaultdict

from lib.config.ConfigParser import ConfigParser
from lib.processing.Processor import Processor

class Executor:
    """
    @author: Gerrald
    @date: 10-12-2025
    """
    def __init__(self, folder_path: str, config: ConfigParser, log: bool = False):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        p = Path(folder_path)
        if not p.exists():
            raise IOError(f"{folder_path} does not exist")
        elif not p.is_dir():
            raise IOError(f"{folder_path} is not a folder")
        files = list(p.glob("*.wav"))
        if len(files) == 0:
            raise IOError(f"{folder_path} does not contain any wav files")
        
        self.folder_path = folder_path
        self.files = files
        self.config = config
        self.log_enabled = log
        self.results = {}
        
    def execute(self, write_enabled: bool = True):
        """
        @author: Gerrald
        @date: 17-12-2025
        """
        for file in self.files:
            self.log(f"Processing {file.stem}")
            processor = Processor(None, self.config, log=self.log_enabled)
            processor.open_file(file)
            try:    
                processor.run(write_enabled=False)
                
                self.results[file] = [len(processor.s1_peaks), len(processor.s2_peaks), len(processor.uncertain), processor]
            except Exception as e:
                self.log(f"{file} failed, Error: {e}")
                
        uncertain_zero = [
            [file, value[0], value[1]]
            for file, value in self.results.items()
            if value[2] == 0
        ]
        
        pairs = defaultdict(list)
        for file, v0, v1 in uncertain_zero:
            pairs[(v0, v1)].append(file)
        
        if len(uncertain_zero) == 0 or len(pairs) > 1:
            print("ERROR: Non-program-solvable challenge, but UI not implemented yet.")
            return
        
        file_used = next(iter(pairs.values()))[0]
        self.log(f"Using {file_used}: s1_peaks:{len(processor.s1_peaks)}, s2_peaks:{len(processor.s2_peaks)}, uncertain:{len(processor.uncertain)}")
        used_peaks_s1 = self.results[file_used][3].s1_peaks
        used_peaks_s2 = self.results[file_used][3].s2_peaks
        
        for file, value in self.results.items():
            processor = value[3]
            
            processor.s1_peaks = used_peaks_s1
            processor.s2_peaks = used_peaks_s2
            
            processor.segment()
            if write_enabled:
                processor.write()
            
        self.log("Finished!")
        
    def summarize(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        print(f"Finished with the following results:")
        for file, r in self.results.items():
            print(f"{file.stem}: s1: {r[0]};  s2: {r[1]}; u: {r[2]}; tot: {sum(r)}")
    def log(self, msg):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        if self.log_enabled:
            print(msg)