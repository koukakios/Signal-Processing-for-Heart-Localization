from pathlib import Path

from lib.config.ConfigParser import ConfigParser
from lib.processing.Processor import Processor

class Executor:
    def __init__(self, folder_path: str, config: ConfigParser, log: bool = False):
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
        
    def execute(self):
        processor = Processor(None, self.config, log=self.log_enabled)
        for file in self.files:
            self.log(f"Processing {file.stem}")
            processor.open_file(file)
            try:
                processor.process()
            except Exception as e:
                self.log(f"{file.stem} failed, Error: {e.with_traceback()}")
        self.log("Finished!")
    def log(self, msg):
        if self.log_enabled:
            print(msg)