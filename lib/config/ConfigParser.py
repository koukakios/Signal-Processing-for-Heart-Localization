import re
from pathlib import Path
from typing import Iterable

from lib.config.ConfigDefaults import *
from lib.config.AttrSection import AttrSection

class ConfigParser:
    """
    @author: Gerrald
    @date: 10-12-2025

    A minimal INI-like configuration parser with comment preservation
    and attribute-style section access.

    This class reads a configuration file, stores its sections, key/value
    pairs, and comments, and provides convenient access to each section via
    dynamically created attributes. Unlike Python's built-in `configparser`,
    this implementation preserves comments and allows round-trip writing.

    Attributes:
        path (Path): Path to the configuration file.
        comments (dict[str, list[str]]): Mapping of section -> list of comment strings.
        config (dict[str, dict[str, Any]]): Parsed configuration data.
    
    """
    
    def __init__(self, path: Path|str = CONFIG_PATH) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Initialize a ConfigParser instance.

        If the configuration file does not exist, a default configuration is
        created using DEFAULT_CONFIG and DEFAULT_COMMENTS. Otherwise, the file
        is read and parsed. For each section, an `AttrSection` wrapper is
        attached as an attribute for dot-style access (e.g., `config.general.key`).

        Args:
            path (Path | str, optional): Path to the configuration file.
                Defaults to CONFIG_PATH.
        
        """
        self.path = Path(path)
        self.comments = {}
        self.config = {}
        
        if not self.path.exists():
            self._create_default()
        else:
            self.read()
            
        for section in self.sections():
            setattr(self, section, AttrSection(section, self.config))
            
    def read(self) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Parse the configuration file from disk.

        Reads the file line-by-line, identifying:
        - Section headers: [section]
        - Key/value pairs: key = value
        - Comments starting with ';' or '#'
        - Empty lines are skipped

        Parsed data is inserted into `self.config` and `self.comments`.
        Unrecognized lines emit a warning.

        Raises:
            FileNotFoundError: If the configuration file cannot be opened.
        
        """
        current_section = ""
        with open(self.path) as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                line = line.strip()
                
                comment = re.match(r"\A[;#]", line)
                section = re.match(r"\A\[([^]]+)\]\Z", line)
                attribute = re.match(r"\A([_a-zA-Z][_a-zA-Z0-9]*)\s*=\s*([\"/\\a-zA-Z0-9. ]+)\Z", line)
                
                if line == "":
                    continue
                elif comment:
                    self.addComment(current_section, line)
                elif section:
                    current_section = section.group(1)
                    self.addSection(current_section)
                elif attribute:
                    key = attribute.group(1)
                    value = attribute.group(2)
                    self.addAttribute(current_section, key, value)
                else:
                    print(f"WARNING: did not recognize {line}, skipping")
                    
    def write(self) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Write the current configuration and comments back to disk.

        Sections are written in the order they appear in `self.config`.
        Comments associated with each section (if any) are written immediately
        after the section header.

        Output format:

            [section]
            # comment line
            key = value

        Raises:
            OSError: If the file cannot be written.
        
        """
        with open(self.path, "w") as fp:
            for section in self.sections():
                fp.write(f"[{section}]\n")
                if section in self.comments:
                    fp.write("\n".join(self.comments[section]) + "\n")
                for key, value in self.config[section].items():
                    fp.write(f"{key} = {value}\n")
                fp.write("\n")
                
    def _create_default(self) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Create a default configuration file.

        Loads `DEFAULT_CONFIG` and `DEFAULT_COMMENTS` from ConfigDefaults.py
        into memory and writes them to disk. This is called automatically
        when the target configuration file does not yet exist.
        
        """
        self.comments = DEFAULT_COMMENTS
        self.config = DEFAULT_CONFIG
        self.write()
        
    def sections(self) -> Iterable[str]:
        """
        @author: Gerrald
        @date: 10-12-2025

        Return a list of all section names.

        Returns:
            Iterable[str]: Names of all sections in the configuration.
        
        """
        return self.config.keys()
    
    def addComment(self, section: str, comment: str) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Attach a comment to the given section.

        Args:
            section (str): The section to which the comment belongs.
            comment (str): The comment line (including the '#' or ';' marker).
        
        """
        if section not in self.comments:
            self.comments[section] = []
        self.comments[section].append(comment)
        
    def addSection(self, section: str) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Ensure that a section exists in the configuration.

        Args:
            section (str): The section name.

        Notes:
            If the section already exists, this method does nothing.
        
        """
        if section not in self.config:
            self.config[section] = {}
            
    def addAttribute(self, section: str, key: str, value: str) -> None:
        """
        @author: Gerrald
        @date: 10-12-2025

        Add a key/value pair to a section with automatic type inference.

        The method attempts to detect numeric types:

            - Integer   -> converted using int()
            - Float     -> converted using float()
            - Otherwise -> stored as a string

        Args:
            section (str): The section to modify.
            key (str): The configuration key.
            value (str): The raw string value parsed from the file.
        
        """
        # Check if it could be a int
        if re.match(r"\A[0-9]+\Z", value):
            self.config[section][key] = int(value)
        elif re.match(r"\A[0-9.]+\Z", value):
            self.config[section][key] = float(value)
        else:
            self.config[section][key] = value