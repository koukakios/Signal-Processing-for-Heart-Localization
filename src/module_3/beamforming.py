import numpy as np
# array response, depends on angle of arrival
def a_lin(theta, M, d, v, f0):
    """Returns the *array response* or *steering vector* for a Uniform Linear Microphone Array

    Args:
        theta (float): angle of arrival
        M (int): number of microphones
        d (float): distance between microphones (m)
        v (float): speed of sound (m/s)
        f0 (float): frequency of wave (Hz)

    Returns:
        np.ndarray: The array response
    """  
    """okay"""
    result = np.array([ np.exp(np.imag(-j*mic*(d/v)*np.sin(theta)*2*np.pi*f0)) for mic in range (M)])

    return result

if __name__ == "__main__":
    pass