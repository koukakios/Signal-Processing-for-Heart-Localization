import numpy as np
import matplotlib as plt
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
    result = np.array([ np.exp(np.imag(0 -1*mic*(d/v)*np.sin(theta)*2*np.pi*f0 *1j)) for mic in range (M)])

    return result

def test_a_lin():
    theta = 30
    M = 3
    d = 1
    v = 343
    f0 = 250

    array_response_vector = a_lin(theta, M, d, v, f0)
    
    print (abs(array_response_vector))

if __name__ == "__main__":
    pass