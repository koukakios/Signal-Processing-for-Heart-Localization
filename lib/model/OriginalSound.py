from pathlib import Path
import io
import csv
from scipy.fft import fft, fftshift
from typing import Tuple
import numpy as np

from lib.processing.Processor import Processor
from lib.os.pathUtils import *
from lib.config.ConfigParser import ConfigParser

class OriginalSound:
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Wrapper for the original sound to make it easier to plot it.
    """
    def __init__(self, file_path: str|Path, config: ConfigParser) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Initialize a wrapper for the original sound.

        Args:
            config (ConfigParser): The config object.
        
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"{file_path} can not be found")
            return
            
        self.config = config
        self.shift = self.shift_init = -2.28
        self.file_path = file_path
        
        self.original_length = None
        self.original_Fs = None
        self.processor = None
        
    def reset(self) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Reset the original sound to the initial values.
        
        """
        self.shift = self.shift_init
        
    def get_sound_init(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        @author: Gerrald
        @date: 10-12-2025

        Get all the properties of the origninal sound, including the frequency spectrum.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray]: y_normalized (the amplitude axis), freq (the frequency axis), Y (the frequency amplitude spectrum)
        
        """
        if self.processor is None or self.processor.y_normalized is None or self.processor.Fs_target is None:
            self.processor = Processor(self.file_path.resolve(), self.config, write_result_processed=False, write_result_raw=False)
            self.processor.preprocess()
        
        self.original_length = len(self.processor.y_normalized)
        self.original_Fs = self.processor.Fs_target
        
        Y = fftshift(fft(self.processor.y_normalized))
        Y = Y/np.max(np.abs(Y))
        freq = np.linspace(-self.processor.Fs_target/2, self.processor.Fs_target/2, len(Y))
        
        return self.processor.y_normalized, freq, Y
    
    def get_time(self) -> np.ndarray:
        """
        @author: Gerrald
        @date: 10-12-2025

        Get the time axis of the original sound.

        Returns:
            np.ndarray: The time axis.
        
        """
        return np.linspace(self.shift, self.shift+self.original_length/self.original_Fs, self.original_length)

    
    def generate_summary(self) -> str:
        """
        @author: Gerrald
        @date: 10-12-2025

        Generate a readable summary of the original sound params.

        Returns:
            str: The summary.
        
        """
        return f"Original:\n  - File: {self.file_path.stem}\n  e- Shift: {self.shift}"
    
    def import_csv(self, file_path: str|Path) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Import the original sound params from a csv file. 
        Only considers the section between `OriginalSound:` and the next `:`

        Args:
            file_path (str | Path): The path to the csv file.
        
        """
        file_path = Path(file_path)
        if not file_path.exists():
            print(f"{file_path} can not be found")
            return

        with open(file_path, newline='') as f:
            self.import_csv_s(f.read())
        
    def import_csv_s(self, contents: str) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Import the original sound params from a csv string.
        Only considers the section between `OriginalSound:` and the next `:`

        Args:
            contents (str): The csv in a string.
        
        """
        # Filter the contents to only contain the correct information (Between 'Model:' and another line ending with ":"/EOF)
        filtered_contents = ""
        correct_section = False
        for line in contents.split("\n"):
            line = line.strip()
            if line == "OriginalSound:" and not correct_section:
                correct_section = True
                continue
            elif line.endswith(":") and correct_section:
                break
            elif correct_section:
                filtered_contents += line + "\n"
        
        
        file = io.StringIO(filtered_contents)

        reader = csv.reader(file)
            
        # Load first part
        header = next(reader)
        values = next(reader)
        try:
            if len(values) != 1 and header != ["shift"]:
                print(f"OriginalSound: Values is not as long as expected (expected: 1, actual: {len(values)}) or the header is wrong. Maybe the csv is from an older version. Header: {header}, Values: {values}")
            
            self.shift = float(values[0])
        except:
            print("An exception occured while loading the first part of the OriginalSound section")
            return

    
    def generate_csv(self) -> str:
        """
        @author: Gerrald
        @date: 10-12-2025

        Generate the csv string for the params of the original sound.

        Returns:
            str: The generated csv string.
        
        """
        contents = [["OriginalSound:"], ["shift"],[str(self.shift)]]
        
        return "\n".join([",".join(c) for c in contents])
    
    def export_csv(self, file_path: str|Path) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Export the params of the original sound to a csv file.

        Args:
            file_path (str | Path): The path to the csv file to export to.
        
        """
        ensure_path_exists(file_path)
                
        with open(file_path, "w") as fp:
            fp.write(self.generate_csv())
            
    def export_readable(self, file_path: str|Path) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Export the readable summary to a file.

        Args:
            file_path (str | Path): The path to the file to export to.
        
        """
        ensure_path_exists(file_path)
        
        with open(file_path, "w") as fp:
            fp.write(self.generate_summary())