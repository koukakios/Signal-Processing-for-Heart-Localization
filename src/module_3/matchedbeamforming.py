import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import write
import winsound
import wave 
import os
def autocorr(th_range, M, d, v, f0):
    SNR = 10
    sigma_n = 10**(-SNR/20); # std of the noise (SNR in dB)
    A = a_lin(th_range, M, d, v, f0); # source direction vectors
    A_H = A.conj().T
    R = np.matmul(A,A_H) # assume equal powered sources
    Rn = np.eye(M,M)*sigma_n**2; # noise covariance
    Rx = R + Rn # received data covariance matrix
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


def matchedbeamforming( th_range, M, d, v, f0):
    
    Rx = autocorr(np.array([0,20]), M, d, v, f0)
    A = a_lin(th_range, M, d, v, f0)
    P =np.array( [  1/(np.matmul(np.matmul(A[:,i].conj().T,np.linalg.inv(Rx)),A[:,i]))   for i in range (len(th_range)) ] )
    print(f"A shape {A.shape}")
    print(f"Complex conjugate shape {A.conj().T.shape}")
    print(f"Rx shape {Rx.shape}")
    print(f"P shape {P.shape}")
    print(f"multiplication shape {np.matmul(A.conj().T,Rx).shape}")
    return P


P = matchedbeamforming(np.array([i for i in range (-90,90)]), 7, 1, 343, 250)
Fs = 44000
#signal1 = np.array([np.random.randint(30) for i in range (100)])
#signal2 = np.array([np.random.randint(30) for i in range (100)])
#signal3 = np.array([np.random.randint(30) for i in range (100)])
#write("file1.wav", Fs, signal1)
#write("file2.wav", Fs, signal3)
#write("file3.wav", Fs, signal2)

file_path = os.path.abspath("file1.wav")
print(f"Trying to play: {file_path}")
winsound.PlaySound(file_path, winsound.SND_FILENAME)
#winsound.PlaySound("file2.wav", winsound.SND_FILENAME)
#winsound.PlaySound("file3.wav", winsound.SND_FILENAME)
plt.figure()
plt.plot(P)
plt.show()




