import subprocess
from pathlib import Path
import re
from datetime import datetime

REPO_ROOT = "."
INDENT = "    "

def check_staged():
    """Returns true if there are staged changes
    """
    cmd = ["git", "diff", "--cached", "--name-only"]
    out = subprocess.check_output(cmd, cwd=REPO_ROOT).decode("utf-8", errors="ignore")
    return not len(out) == 0

def get_diff(file, staged: bool = False):
    cmd = ["git", "diff", "--unified=0", str(file)]
    if staged: cmd.insert(2, "--cached")
    out = subprocess.check_output(cmd, cwd=REPO_ROOT).decode("utf-8", errors="ignore")
    
    changed_lines = []
    current_new_line = None
    
    for line in out.splitlines():
        if line.startswith('@@'):
            m = re.search(r'\+(\d+)(?:,(\d+))?', line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2)) if m.group(2) else 1
                current_new_line = start
        elif line.startswith('+') and not line.startswith('+++'):
            # Added line
            changed_lines.append(current_new_line)
            current_new_line += 1
        elif line.startswith('-') and not line.startswith('---'):
            # Removed line (from old file)
            # parse old hunk info if needed
            pass
        elif current_new_line is not None:
            # Context line, advance line counter
            current_new_line += 1

    return changed_lines

def get_whitespace_len(s):
    if s.strip() == "":
        return 10000
    m =  re.match(r"^(?P<indent>\s*)", s)
    if m and m.group("indent"):
        return len(m.group("indent"))
    return 0

def get_whitespace_len_with_key(s, key):
    m =  re.match(rf"^(?P<indent>\s*){key}", s)
    if m:
        return len(m.group("indent"))
    return -1
    
def add_dict_list(d, key, value):
    if not key in d:
        d[key] = [value]
    else:
        d[key].append(value)
        
def get_changed(meta, indents, diffs):
    result = []
    for m_key, m_val in meta.items():
        # Check if m_val is a valid indent key
        if m_val in indents:
            ranges = indents[m_val]
            # Check if any diff falls within any of the ranges
            for r_start, r_end in ranges:
                if any(r_start <= d <= r_end for d in diffs) and r_start <= m_key <= r_end:
                    result.append(m_key)
                    break
    return result
        
def get_git_name():
    name  = subprocess.run(["git", "config", "user.name"],  capture_output=True, text=True).stdout.strip()
    return name
    
def update_file(file, is_staged: bool = False):
    meta_lines = {}
    author_lines = {}
    date_lines = {}
    with open(file) as fp:
        content = fp.read()
        
    content_list = content.splitlines()
    
    indents = {}
    for i, line in enumerate(content_list):
        m =  re.match(r"^(?P<indent>\s*)(def|class)\s+\w+\s*", line)
        if m:
            indent = get_whitespace_len(content_list[i+1])
            for j, next_line in enumerate(content_list[i+1:]):
                if get_whitespace_len(next_line) < indent:
                    break
            add_dict_list(indents, indent, (i+1,i+j+1))
            
        indent = get_whitespace_len_with_key(line, "@meta")
        if indent >= 0:
            meta_lines[i+1] = indent
            
        indent = get_whitespace_len_with_key(line, "@author")
        if indent >= 0:
            author_lines[i+1] = indent
            
        indent = get_whitespace_len_with_key(line, "@date")
        if indent >= 0:
            date_lines[i+1] = indent
            
    diffs = get_diff(file, is_staged)

    meta_changed = get_changed(meta_lines, indents, diffs)
    date_changed = get_changed(date_lines, indents, diffs)
    author_changed = get_changed(author_lines, indents, diffs)
    
    for ac in author_changed:
        content_list[ac-1] = f"{' '*author_lines[ac]}@author: {get_git_name()}"
    for dc in date_changed:
        content_list[dc-1] = f"{' '*date_lines[dc]}@date: {datetime.today().strftime("%d-%m-%Y")}"
    
    n_inserted = 0
    for mc in meta_changed:
        mc_index = mc + n_inserted
        content_list[mc_index-1] = f"{' '*meta_lines[mc]}@author: {get_git_name()}"
        content_list.insert(mc_index-1, f"{' '*meta_lines[mc]}@date: {datetime.today().strftime("%d-%m-%Y")}")
        n_inserted += 1
    
    content = "\n".join(content_list)
    with open(file, "w") as fp:
        fp.write(content)
    print(f"Updated {str(file)}")
    # for line, indent in indents.items():
        

def main():
    file = Path("src\\module_2\\old\\matchParamsV2.py")
    files = [
        file
        for file in Path(".").rglob("*.py")
    ]
    any_staged = check_staged()
    for file in files:
        if "tools" in str(file):
            continue
        update_file(file, any_staged)
    
if __name__ == "__main__":
    main()