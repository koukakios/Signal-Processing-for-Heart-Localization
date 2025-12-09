import numpy as np
import matplotlib.pyplot as plt

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
    result = np.array([ np.exp(-1*mic*(d/v) * np.sin(theta*np.pi/180)*2* np.pi*f0 *1j) for mic in range (M)])

    return result


def MVDR( th_range, M, d, v, f0, Rx):
    
    A = a_lin(th_range, M, d, v, f0)
    P =np.array( [  1/(np.matmul(np.matmul(A[:,i].conj().T,np.linalg.inv(Rx)),A[:,i]))   for i in range (len(th_range)) ] )
    print(f"A shape {A.shape}")
    print(f"Complex conjugate shape {A.conj().T.shape}")
    print(f"Rx shape {Rx.shape}")
    print(f"P shape {P.shape}")
    print(f"multiplication shape {np.matmul(A.conj().T,Rx).shape}")
    return P


def find_MVDR_beamformer (th_range, M, d, v, fo, Rx):
    
    A = a_lin(th_range, M, d, v, f0)
    P =np.array( [  (np.matmul(np.linalg.inv(Rx), A[:,i]) ) /
                  (np.matmul(np.matmul(A[:,i].conj().T,np.linalg.inv(Rx)),A[:,i]))   
                  for i in range (len(th_range)) ] )
    return P              

M = 7
v = 343
f0 = 250
D = 0.5
lamda = v/f0
d = D*lamda
Rx = autocorr(np.array([0,15]), M, d, v, f0)
theta_range = np.array([i for i in range (-90,90)])
P = MVDR(theta_range, M, d, v, f0, Rx)
w = find_MVDR_beamformer(theta_range, M, d, v, f0, Rx)


plt.figure()
x = np.arange(-90,90);
plt.plot(x,w)
plt.show()




