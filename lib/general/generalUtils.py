import numpy as np

def todB(value: float|list|np.ndarray, power: bool = False):
    """Convert a value from linear to dB.

    Args:
        value (float | list | np.ndarray): The value(s) to convert.
        power (bool, optional): Whether the value is a power value. If true, the result is 10 * log10(value), else 20 * log10(value). Defaults to False.

    Returns:
        float | list | np.ndarray: The dB values of the input.
    """
    return 10 * np.log10(value) * (1 if power else 2)
    
def fromdB(dB: float|list|np.ndarray, power: bool = False):
    """Convert a value from dB to linear.

    Args:
        dB (float | list | np.ndarray): The dB value(s) to convert.
        power (bool, optional): Whether the value is a power value. If true, the result is 10 ^ (dB/10), else 10 ^ (dB/20). Defaults to False.

    Returns:
        float | list | np.ndarray: The linear values of the input.
    """
    return 10 ** (dB / (10 if power else 20))