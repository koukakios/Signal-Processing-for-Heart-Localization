import numpy as np
import matplotlib.pyplot as plt
# array response, depends on angle of arrival
def a_lin(theta, M, d, v, f0):
    """
    @author: Gerrald
    @date: 10-12-2025

    Returns the *array response* or *steering vector* for a Uniform Linear Microphone Array

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
    result = np.array([ np.exp((0 -1*mic*(d/v)*np.sin(theta*np.pi/180)*2*np.pi*f0 *1j)) for mic in range (M)])

    return result

def test_a_lin():
    theta = 0
    M = 7
    d = 1
    v = 343
    f0 = 500

    array_response_vector = a_lin(theta, M, d, v, f0)
    
    print (abs(array_response_vector))

def spatial_spectrum(theta0):
    
    M = 7
    d = 1
    v = 340
    f0 = 500
    
    power_out = np.array([ ( np.abs ((  np.dot(a_lin(theta, M, d, v, f0).conj().T,
                          a_lin(theta0, M, d, v, f0))   )))**2 for theta in range (-90,90,1)  ]   )
    
    x = np.arange(-90,90)
    y = power_out
    plt.plot(x,y)
    plt.xlabel("angle in degress")
    plt.ylabel("power out")
    plt.show()

if __name__ == "__main__":
    spatial_spectrum(0)