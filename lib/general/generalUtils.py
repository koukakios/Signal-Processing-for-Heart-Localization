import numpy as np
from random import random

def todB(value: float|list|np.ndarray, power: bool = False) -> float | list | np.ndarray:
    """
    @author: Gerrald
    @date: 10-12-2025

    Convert a value from linear to dB.

    Args:
        value (float | list | np.ndarray): The value(s) to convert.
        power (bool, optional): Whether the value is a power value. If true, the result is 10 * log10(value), else 20 * log10(value). Defaults to False.

    Returns:
        float | list | np.ndarray: The dB values of the input.
    
    """
    return 10 * np.log10(value) * (1 if power else 2)
    
def fromdB(dB: float|list|np.ndarray, power: bool = False) -> float | list | np.ndarray:
    """
    @author: Gerrald
    @date: 10-12-2025

    Convert a value from dB to linear.

    Args:
        dB (float | list | np.ndarray): The dB value(s) to convert.
        power (bool, optional): Whether the value is a power value. If true, the result is 10 ^ (dB/10), else 10 ^ (dB/20). Defaults to False.

    Returns:
        float | list | np.ndarray: The linear values of the input.
    
    """
    return 10 ** (dB / (10 if power else 20))

def randomize(val: float, ratio: float) -> float:
    """
    @author: Gerrald
    @date: 10-12-2025
    
    Randomize a value.

    Args:
        val (float): The value to randomize
        ratio (float): The max random component in ratio of the value.

    Returns:
        float: The randomized value.
    """
    return val * (1 + ratio * random())