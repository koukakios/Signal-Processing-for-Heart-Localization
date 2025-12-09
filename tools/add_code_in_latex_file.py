from pathlib import Path

def overlize(s):
    return str(s).replace("\\", "/")

include_paths = ["./src", "./lib"]
include_extensions = ["*.py", "*.ini"]
exclude = ["NoCommit_", "*/old/"]

files = [
    file
    for base in include_paths
    for pattern in include_extensions
    for file in Path(base).rglob(pattern)
    if not any(file.match(ex) for ex in exclude)
]

root = Path(".")

with open("NoCommit_Latex_include_code.tex", "w") as fp:
    for file in files:
        path = file.relative_to(root)
        parent_path = path.parent
        fp.write(f"""\\section{{{overlize(parent_path)}}}
\\subsection{{{overlize(path)}}}
\\lstinputlisting{{../../../{overlize(path)}}}\n""")