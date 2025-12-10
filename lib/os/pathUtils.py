from os import listdir
from pathlib import Path

def get_files_ext(ext:str, dir:str=".") -> list:
    """
    @author: Gerrald
    @date: 10-12-2025

    Gets files in a certain directory with a certain extension.

    Args:
        ext (str): The extension of the file you are searching for.
        dir (str, optional): The path you are searching the file in. Defaults to ".".

    Returns:
        list: A list of the filenames in the directory that end with the given extension.
    
    """
    return [file for file in listdir(dir) if file.endswith(ext)] 
    
def ensure_path_exists(file_path: Path|str, is_parent: bool = False) -> None:
    """
    @author: Gerrald
    @date: 10-12-2025

    Make sure the path to a file/folder exists.

    Args:
        file_path (Path | str): The path to the file/folder.
        is_parent (bool, optional): Whether the given path should be verified itself (is a parent). If False, only verify till the parent path. Defaults to False.
    
    """
    file_path = Path(file_path)
    if not is_parent:
        file_path = file_path.resolve().parent
    file_path.mkdir(parents=True, exist_ok=True)