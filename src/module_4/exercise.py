import numpy as np


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
    result = np.array([ np.exp((0 -1*mic*(d/v)*np.sin(theta*np.pi/180)*2*np.pi*f0 *1j)) for mic in range (M)])

    return result

def generate_source(N):
    
    
    s_real = np.random.randn(N)
    s_imag = np.random.randn(N)
    
    
    s = s_real + 1j * s_imag
    
    
    # Power is defined as E[|s|^2], estimated by mean(|s|^2)
    current_power = np.mean(np.abs(s)**2)
    s_normalized = s / np.sqrt(current_power)
    
    return s_normalized

def datamodel (M, N, theta0, d, v, f0):
    
    

    A = np.array([a_lin(theta0[i], M, d, v, f0) for i in range (len(theta0)) ] )
    A = np.transpose(A)
    S = np.array([generate_source(N) for i in range (len(theta0))])
    print(A.shape)
    print(S.shape)
    X = np.matmul(A,S)
    print (np.linalg.matrix_rank(X))
    return X

if __name__ == "__main__":
    M = 7
    N = 6
    theta0 = [10,22,11,40,-10,56]
    d = 0.1
    v = 343
    f0 = 250

    X = datamodel(M, N, theta0, d, v, f0)
    rankx = np.linalg.matrix_rank(X)
    print(rankx)
    print (X.shape)
    U, S, Vh = np.linalg.svd(X)
    V = Vh.conj().T
    print (S.shape)   