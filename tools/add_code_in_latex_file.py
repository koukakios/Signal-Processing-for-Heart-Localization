from pathlib import Path

def overlize(s: Path, is_path=False):
    if str(s) == ".":
        return "Project Root"
    if is_path:
        return str(s).replace("\\", "/")
    else:
        return str(s).replace("\\", "/").replace("_", "\\_")
    
def get_command(path: Path):
    match path.suffix:
        case ".py":
            return "pythonfile"
        case ".ini":
            return "inifile"
        case _:
            return "undefined"
        
def get_unique_label(path: Path, labels: list[str]) -> str:
    name = path.stem
    test = name
    i = 0
    while test in labels:
        test = f"{path.parent.stem}-{name}" + (f"-{i}" if i > 0 else "")
        i += 1
    labels.append(test)
    return test
    

include_paths = ["./src", "./lib"]
include_extensions = ["*.py", "*.ini"]
exclude = ["NoCommit_", "\\old\\", "__init__"]

files = [
    file
    for base in include_paths
    for pattern in include_extensions
    for file in Path(base).rglob(pattern)
    if not any(ex in str(file) for ex in exclude)
]

files.insert(0, Path("config.ini"))

root = Path(".")
previous_parent_path = None
labels = []
with open("NoCommit_Latex_include_code.tex", "w") as fp:
    fp.write("\\chapter{Code}\n\n")

    for file in files:
        path = file.relative_to(root)
        parent_path = path.parent
        
        if parent_path != previous_parent_path:
            fp.write(f"""\\section{{{overlize(parent_path)}}}\n""")
            previous_parent_path = parent_path
        fp.write(f"""\\subsection*{{{overlize(path)}}}
\\label{{ap:{get_unique_label(path, labels)}}}
\\{get_command(path)}{{../../../{overlize(path, is_path=True)}}}\n""")