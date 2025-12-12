from pathlib import Path

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
        
    def execute(self):
        """
        @author: Gerrald
        @date: 10-12-2025
        """
        processor = Processor(None, self.config, log=self.log_enabled)
        for file in self.files:
            self.log(f"Processing {file.stem}")
            processor.open_file(file)
            try:
                processor.run()
                
                self.results[file] = [len(processor.s1_peaks), len(processor.s2_peaks), len(processor.uncertain)]
            except Exception as e:
                self.log(f"{file} failed, Error: {e}")
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