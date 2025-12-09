from os import listdir
from pathlib import Path

def getFilesExt(ext:str, dir:str="."):
    """Gets files in a certain directory with a certain extension

    Args:
        ext (str): The extension of the file you are searching for.
        dir (str, optional): The path you are searching the file in. Defaults to ".".

    Returns:
        list: A list of the filenames in the directory that end with the given extension.
    """
    return [file for file in listdir(dir) if file.endswith(ext)] 

def ensurePathExists(path: str | Path):
    Path(path).mkdir(parents=True, exist_ok=True)