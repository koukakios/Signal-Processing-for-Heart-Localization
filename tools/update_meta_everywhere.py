from pathlib import Path
import re

author = "Gerrald"
date = "10-12-2025"

files = [
    file
    for file in Path(".").rglob("*.py")
]

print(f"{len(files)} files")

for file in files:
    if "tools" in str(file):
        continue
    with open(file) as fp:
        contents = fp.read()
    
    updated_contents = []
    for line in contents.split("\n"):
        if "@author" in line or "@date" in line:
            updated_contents.append(line)
            continue
        if not ("@meta" in line):# or "@author" in line or "@date" in line ):
            updated_contents.append(line)
            continue
        
        m = re.match(r"^(?P<indent>\s*)", line)
        
        indent = m.group("indent")
        updated_contents.append(f"{indent}@author: {author}")
        updated_contents.append(f"{indent}@date: {date}")
        
        
        
    changed_contents = "\n".join(updated_contents)
    
    if changed_contents != contents:
        with open(file, "w") as fp:
            fp.write(changed_contents)
            print(f"Changed {str(file)}")
    else:
        print(f"Skipped {str(file)}")
        