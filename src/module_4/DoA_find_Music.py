import numpy as np
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import gaussian
from scipy.io import wavfile
from pathlib import Path
import matplotlib.pyplot as plt
import soundfile as sf
from exercise import a_lin

def music(X, Q, M, d, v, f0):

    # X shape: (M, T)
    Rx = (X @ X.conj().T) / X.shape[1]

    eigvals, eigvecs = np.linalg.eigh(Rx)  
    Un = eigvecs[:, :M-Q]                   

    angles = np.linspace(-90, 90, 360)
    P = []

    for angle in angles:
        a = a_lin(angle, M, d, v, f0).reshape(M,1)
        denom = a.conj().T @ Un @ Un.conj().T @ a
        P.append(1.0 / np.abs(denom[0,0]))

    return np.array(P)



if __name__ == "__main__":
    fs = 48000
    win = ('gaussian', 1e-2 * fs)
    SFT = ShortTimeFFT.from_window(win, fs, nperseg = 256 ,noverlap=0, scale_to='magnitude', phase_shift=None)
    #path2source = Path(r"C:\Users\kkouk\IP3\2 source, distance 7 meter, microphone stand at 0 degrees, speaker at 7 degrees left and right.wav")
    filepath1 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_1.wav")
    filepath2 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_2.wav")
    filepath3 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_3.wav")
    filepath4 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_4.wav")
    filepath5 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_5.wav")
    filepath6 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_6.wav")
    
    #sources, rate = sf.read(path2source)
    rate, signal1 = wavfile.read(filepath1)
    rate, signal2 = wavfile.read(filepath2)
    rate, signal3 = wavfile.read(filepath3)
    rate, signal4 = wavfile.read(filepath4)
    rate, signal5 = wavfile.read(filepath5)
    rate, signal6 = wavfile.read(filepath6)
    print ("ayo")
    #print (sources.shape)
    print(signal1.shape)

    #signal1 = sources[:,0]
    #signal2 = sources[:,1]
    #signal3 = sources[:,2]
    #signal4 = sources[:,3]
    #signal5 = sources[:,4]
    #signal6 = sources[:,5]
    

    
    Sx1 = SFT.stft(signal1)
    Sx2 = SFT.stft(signal2)
    Sx3 = SFT.stft(signal3)
    Sx4 = SFT.stft(signal4)
    Sx5 = SFT.stft(signal5)
    Sx6 = SFT.stft(signal6)

    Sx_all=np.stack((Sx1,Sx2,Sx3,Sx4,Sx5,Sx6))
    
    #print (Sx1.shape)
    print(Sx_all.shape)

    f_bins = SFT.f

    Delta_f = f_bins[1] - f_bins[0]
    print( Delta_f)
    bin = 12
    central_freq = bin*Delta_f
    X = Sx_all[:,bin , :]
    print(X.shape)
    print(central_freq)

    Q = 2
    M = 6
    v = 343
    f0 = central_freq
    d = 0.10
    Pout = music (X, Q, M, d, v, f0)
    angles = np.linspace(-90, 90, 360)

    plt.figure(figsize=(8,4))
    plt.plot(angles, np.abs(Pout), linewidth=2)

    ymax = np.max(np.abs(Pout))

    # vertical lines at the two source angles (now red)
    plt.axvline(55.181, linestyle='--', color='red')
    #plt.axvline(6.22,  linestyle='--', color='red')

    # labels, slightly shifted so they don't overlap
    plt.text(55.181 -3, ymax - 1, "55.181°",
             ha='right', va='bottom', fontsize=13, color='red')
    #plt.text(6.22 + 3,  ymax - 1, "6.22°",
             #ha='left', va='bottom', fontsize=10, color='red')

    plt.xlabel("Angle (degrees)", fontsize=12)
    plt.ylabel("MUSIC Spectrum", fontsize=12)
    plt.title("MUSIC Spectrum (1 source at 60°) / Bin Frequency = 1687 Hz" , fontsize=13)

    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()



