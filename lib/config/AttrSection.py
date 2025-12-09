class AttrSection:
    """Attribute-style access wrapper for a configuration section.

    This class allows accessing configuration keys as Python attributes,
    e.g. `config.general.username`, while reading/writing the underlying
    dictionary that stores the section's key/value pairs.

    Attribute names beginning with an underscore are treated as internal
    attributes and stored normally. All other attributes are redirected
    to the configuration dictionary.
    """
    
    def __init__(self, section_name: str, config: dict):
        """Initialize an attribute wrapper for a configuration section.

        Args:
            section_name (str): The name of the section this object wraps.
            config (dict): Reference to the main configuration dictionary.
                Expected shape: {section: {key: value, ...}}.
        """
        self._section = section_name
        self._config = config
        
    def __getattr__(self, name):
        """Retrieve a configuration value as an attribute.

        Args:
            name (str): The key name being accessed.

        Returns:
            Any: The stored value for the given key.

        Raises:
            AttributeError: If the key does not exist in this section.
        """
        if name in self._config[self._section]:
            return self._config[self._section][name]
        raise AttributeError(f"No such field '{name}' in section '{self._section}'")
    
    def __setattr__(self, name, value):
        """Assign a configuration value via attribute syntax.

        If the attribute name begins with an underscore, it is treated as
        an internal attribute and assigned normally. Otherwise, the key is
        stored in the parent configuration dictionary.

        Args:
            name (str): The key being assigned.
            value (Any): The value to store.
        """
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            self._config[self._section][name] = str(value)
            
    def keys(self):
        """Return all configuration keys in this section.

        Returns:
            list[str]: A list of key names for this section.
        """
        return list(self._config[self._section].keys())