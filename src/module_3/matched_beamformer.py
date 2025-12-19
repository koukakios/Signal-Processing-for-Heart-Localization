import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import winsound
import wave 
import os
def autocorr(th_range, M, d, v, f0):
    SNR = 10
    sigma_n = 10**(-SNR/20)

    A = np.array([a_lin(angle, M, d, v, f0) for angle in th_range]).T  # (M,Q)
    R = A @ A.conj().T                                                 # (M,M)

    Rn = (sigma_n**2) * np.eye(M)                                      # (M,M)
    Rx = R + Rn
    return Rx


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
    result = np.array([ np.exp(-1*mic*(d/v)*np.sin(theta*np.pi/180)*2*np.pi*f0 *1j) for mic in range (M)])

    return result


def matchedbeamforming(th_range, M, d, v, f0, Rx):
    
    #Rx = autocorr(th_range, M, d, v, f0)
    P = np.array([np.matmul(np.matmul(a_lin(angle, M, d, v, f0).conj().T , Rx), a_lin(angle, M, d, v, f0) ) for angle in th_range])
    #P =np.array( [  1/(np.matmul(np.matmul(A[:,i].conj().T,np.linalg.inv(Rx)),A[:,i]))   for i in range (len(th_range)) ] )
    #print(f"A shape {A.shape}")
    #print(f"Complex conjugate shape {A.conj().T.shape}")
    #print(f"Rx shape {Rx.shape}")
    #print(f"P shape {P.shape}")
    #print(f"multiplication shape {np.matmul(A.conj().T,Rx).shape}")
    return P

def test_matched_beamforming():
    M = 7
    Delta = 0.5
    v = 340
    f0 = 500
    d = (v*Delta/f0)
    theta0 = np.array([0,15])
    Rx = autocorr(theta0, M, d, v, f0)

    th_range = np.arange(-90,90)
    P = matchedbeamforming(th_range, M, d, v, f0, Rx)

    theta = np.arange(-90,90)
    plt.plot(theta, P)
    plt.xlabel("angle [deg]")
    plt.title("spacial response for fixed beamformer")
    plt.text(-85, 40, f"M={M}\nDelta={Delta}\ntheta=[0,15]")
    plt.show()

if __name__ == "__main__":
    test_matched_beamforming()





