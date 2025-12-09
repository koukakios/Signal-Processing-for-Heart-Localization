from pathlib import Path

def ensure_path_exists(file_path: Path|str, is_parent: bool = False):
    """Make sure the path to a file/folder exists

    Args:
        file_path (Path | str): The path to the file/folder
        is_parent (bool, optional): Whether the given path should be verified itself (is a parent). If False, only verify till the parent path. Defaults to False.
    """
    file_path = Path(file_path)
    if not is_parent:
        file_path = file_path.resolve().parent
    file_path.mkdir(parents=True, exist_ok=True)