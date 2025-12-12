import numpy as np
from exercise import a_lin
from exercise import generate_source
from exercise import datamodel
from autocorrelation import autocorr
import matplotlib.pyplot as plt

def fake_music (Rx, Q, M, th_range, d, v, f0, N):
    X = datamodel (M, N, th_range, d, v, f0)
    U, S, Vh = np.linalg.svd(X)
    Un = U[:,Q:]
    print ("in music")
    print(U.shape)
    print(Q)
    print(Un.shape)

    angles_to_try = np.array([i for i in range (-90,90)])
    
    Pmusic = np.array([1 / (np.matmul (np.matmul(np.matmul(a_lin(angle, M, d, v, f0).conj().T, Un), Un.conj().T) , a_lin(angle, M, d, v, f0) ))   
                       for angle in angles_to_try])
    return Pmusic

def music (X, Q, M, d, v, f0):
    Rx = (1/len(X))*np.matmul(X, X.conj().T)
    eigenvals, eigenvecs = np.linalg.eigh(Rx)
    noises = M - Q
    Un = eigenvecs[:, :noises]
    
    angles_to_try = np.array([i for i in range (-90,90)])
    
    Pmusic = np.array([1 / (np.matmul (np.matmul(np.matmul(a_lin(angle, M, d, v, f0).conj().T, Un), Un.conj().T) , a_lin(angle, M, d, v, f0) ))   
                       for angle in angles_to_try])
    return Pmusic



if __name__ == "__main__":
    #define parameters
    th_range = np.array([0,15]) 
    M = 7
    v = 343
    f0 = 250
    D = 0.5
    lamda = v/f0
    d = D*lamda
    Q = len(th_range)
    N = 100

    #find autocorellation
    Rx = autocorr(th_range, M, d, v, f0)

    #call music
    #Pmusic = fake_music(Rx, Q, M, th_range, d, v, f0, N)
    X = datamodel (M, N, th_range, d, v, f0)
    Pmusic = music(X, Q, M, d, v, f0)
    angles = np.arange(-90,90)
    plt.plot(angles,Pmusic)
    plt.show()
    