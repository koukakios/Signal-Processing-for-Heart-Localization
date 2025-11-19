import numpy as np
#wrt to 1
def todB(value: float|list|np.ndarray, power: bool = False):
    return 10 * np.log10(value) * (1 if power else 2)
    
def fromdB(dB: float|list|np.ndarray, power: bool = False):
    return 10 ** (dB / (10 if power else 20))