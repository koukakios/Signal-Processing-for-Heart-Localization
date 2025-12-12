from copy import deepcopy
from pathlib import Path
import csv
import io
from scipy.fft import fft, fftshift
from typing import Tuple
from scipy.io.wavfile import write
from os.path import join

from lib.config.ConfigParser import ConfigParser
from lib.model.generate import *
from lib.os.pathUtils import *

class Model:
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Wrapper for the original sound to make it easier to plot it.
    """
    def __init__(self, config: ConfigParser, randomize_enabled: bool = False) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Initialize a wrapper for the model.

        Args:
            config (ConfigParser): The config object.
            randomize_enabled (bool): Whether to randomize the parameters a bit to check robustness of the algorithm.
        
        """
        self.Fs = config.HeartSoundModel.Fs
        self.len_g = config.LowpassFilter.Size
        self.lf = config.LowpassFilter.LowFrequency
        self.hf = config.LowpassFilter.HighFrequency
        self.order = config.LowpassFilter.FilterOrder
        self.size = config.LowpassFilter.Size
        
        self.sounds_path = config.Generation.SoundsPath
        
        self.randomize_enabled = randomize_enabled
        
        self.n = self.n_init = 10
        self.BPM = self.BPM_init = config.HeartSoundModel.BPM
        self.shift = self.shift_init = -2.28
        self.valves_init = [
            ValveParams( 10, 30, 10, 10, 0.05, 0.1,   1,  50,  50, "M"), 
            ValveParams( 40, 30, 10, 10, 0.05, 0.1, 0.5, 150, 150, "T"), 
            ValveParams(300, 30, 10, 10, 0.05, 0.1, 0.5,  50,  50, "A"), 
            ValveParams(330, 30, 10, 10, 0.05, 0.1, 0.4,  30,  30, "P"), 
        ]
        self.valves = deepcopy(self.valves_init)
        
    def reset(self) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Reset the model to the initial values.
        
        """
        self.n = self.n_init
        self.BPM = self.BPM_init
        self.valves = deepcopy(self.valves_init)
    
    def generate_summary(self) -> str:
        """
        @author: Gerrald
        @date: 10-12-2025

        Generate a readable summary of the model.

        Returns:
            str: The summary.
        
        """
        s = ""
        s += f"""Model:\n  - BPM: {self.BPM}\n  - n: {self.n}\n  - Valves:\n"""
        for valve in self.valves:
            s += ("      - " + "\n        ".join(valve.toStr())+"\n")
        return s
    
    def save(self, file_path: str|None = None) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Writes the model as a sound file in the path given in the config.
        
        Args:
            file_path (str | None): If specified, write to that file, otherwise write to standard file.
        
        """
        wav_path = file_path if file_path is not None else join(self.sounds_path, f"Advanced-{self.Fs}Hz-{self.BPM}BPM-{self.n} beats.wav")
        
        ensure_path_exists(wav_path)
        
        t_model, h_model = self.generate_model()
        
        write(wav_path, self.Fs, h_model)
    
    def generate_model(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        @author: Gerrald
        @date: 10-12-2025

        Generates the model time and amplitude axis.

        Returns:
            Tuple[np.ndarray, np.ndarray]: t_model (the time axis), h_model (the amplitude axis).
        
        """
        t_model, h_model = advanced_model(
            self.Fs,
            self.BPM,
            self.lf,
            self.hf,
            self.order,
            self.size,
            self.valves,
            self.n, 
            randomize_enabled=self.randomize_enabled,
            noise=0.01
        )
        
        return t_model, h_model
    
    def generate_model_and_freq(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        @author: Gerrald
        @date: 10-12-2025

        Generates the model time, amplitude and frequency axis.

        Returns:
            Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]: t_model (the time axis), h_model (the amplitude axis), freq (the frequency axis), H (the frequency amplitude spectrum)
        
        """
        t_model, h_model = self.generate_model()
        
        H = fftshift(fft(h_model))
        H = H/np.max(np.abs(H))
        freq = np.linspace(-self.Fs/2, self.Fs/2, len(H))
        
        return t_model, h_model, np.array(freq), np.array(H)
    
    def import_csv(self, file_path: str|Path) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Import the model from a csv file.
        Only considers the section between `Model:` and the next `:`

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

        Import the model from a csv string.
        Only considers the section between `Model:` and the next `:`

        Args:
            contents (str): The csv in a string.
        
        """
        # Filter the contents to only contain the correct information (Between 'Model:' and another line ending with ":"/EOF)
        filtered_contents = ""
        correct_section = False
        for line in contents.split("\n"):
            line = line.strip()
            if line == "Model:" and not correct_section:
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
            if len(values) != 2 and header != ["BPM","n"]:
                print(f"Model: Values is not as long as expected (expected: 2, actual: {len(values)}) or the header is wrong. Maybe the csv is from an older version. Header: {header}, Values: {values}")
            
            self.BPM = int(values[0])
            self.n = int(values[1])
        except:
            print("An exception occured while loading the first part of the model section")
            return
            
        # Second part
        lower_header = next(reader)
        if lower_header != ["name","delay","duration_total","duration_onset","a_onset","a_main","ampl_onset","ampl_main","freq_onset","freq_main"]:
            print(f'Model: The header is not as expected (expected: "name","delay","duration_total","duration_onset","a_onset","a_main","ampl_onset","ampl_main","freq_onset","freq_main", actual: {lower_header}). Maybe the csv is from an older version')
        try:
            self.valves = []
            for row in reader:
                if not row:
                    continue
                self.valves.append(
                    ValveParams(
                        name=row[0],
                        delay_ms=float(row[1])*1000,
                        duration_total_ms=float(row[2])*1000,
                        duration_onset_ms=float(row[3])*1000,
                        a_onset=float(row[4]),
                        a_main=float(row[5]),
                        ampl_onset=float(row[6]),
                        ampl_main=float(row[7]),
                        freq_onset=float(row[8]),
                        freq_main=float(row[9])
                    )
                )
        except:
            print("An exception occured while loading the second part of the model section")
            return
        
    def set_n(self, n: int) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Sets the amount of beats to a different value.

        Args:
            n (int): The amount of beats to generate.
        
        """
        self.n = n
    
    def generate_csv(self) -> str:
        """
        @author: Gerrald
        @date: 10-12-2025

        Generate the csv string for the params of the model.

        Returns:
            str: The generated csv string.
        
        """
        contents = [["Model:"], ["BPM", "n"], [str(self.BPM), str(self.n)], [self.valves[0].properties()]]
        for valve in self.valves:
            contents.append(valve.values_str())
        
        return "\n".join([",".join(c) for c in contents])
    
    def export_csv(self, file_path: str|Path) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Export the params of the model to a csv file.

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