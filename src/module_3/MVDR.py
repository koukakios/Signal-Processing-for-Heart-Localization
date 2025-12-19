import numpy as np
import matplotlib.pyplot as plt

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


def find_MVDR_beamformer(theta0, M, d, v, f0, Rx):
    a0 = a_lin(theta0, M, d, v, f0).reshape(M, 1)      
    Rx_inv = np.linalg.inv(Rx)
    w = (Rx_inv @ a0) / (a0.conj().T @ Rx_inv @ a0)    
    return w.flatten()                                 
              

def test_MVDR ():
    M = 7
    Delta = 0.5
    v = 340
    f0 = 500
    d = (v*Delta/f0)
    theta0 = np.array([0,15])
    Rx = autocorr(theta0, M, d, v, f0)

    th_range = np.arange(-90,90)
    P = MVDR( th_range, M, d, v, f0, Rx)
    theta = np.arange(-90,90)
    plt.plot(theta, P)
    plt.xlabel("angle [deg]")
    plt.title("spacial response for MVDR")
    plt.text(-85, 0.6, f"M={M}\nDelta={Delta}\ntheta=[0,15]")
    plt.show()



def test_MVDR_beamformer():
    M = 7
    Delta = 0.5
    v = 340
    f0 = 500
    d = (v*Delta/f0)
    theta0 = np.array([0,15])
    Rx = autocorr(theta0, M, d, v, f0)

    w = find_MVDR_beamformer(15, M, d, v, f0, Rx)

    th_range = np.arange(-90,90)
    resp = np.array([np.abs(w.conj().T @ a_lin(th, M, d, v, f0)) for th in th_range])

    plt.plot(th_range, resp)
    plt.xlabel("angle [deg]")
    plt.title("Beamformer Amplitude")
    plt.text(-85, 0.6, f"M={M}\nDelta={Delta}\ntheta=15")
    plt.show()

if __name__ == "__main__":
    test_MVDR_beamformer()






