import numpy as np
from matched_beamformer import matchedbeamforming
from MVDR import MVDR
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import gaussian
from scipy.io import wavfile
from pathlib import Path
import matplotlib.pyplot as plt
import soundfile as sf
#README FOR REPORT. So like 

if __name__ == "__main__":
    fs = 48000
    win = ('gaussian', 1e-2 * fs)
    SFT = ShortTimeFFT.from_window(win, fs, nperseg = 256 ,noverlap=0, scale_to='magnitude', phase_shift=None)
    path2source = Path(r"C:\Users\kkouk\IP3\2 source, distance 7 meter, microphone stand at 0 degrees, speaker at 7 degrees left and right.wav")
    #filepath1 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_1.wav")
    #filepath2 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_2.wav")
    #filepath3 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_3.wav")
    #filepath4 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_4.wav")
    #filepath5 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_5.wav")
    #filepath6 = Path(r"C:\Users\kkouk\IP3\Project-Heart-EE2L1\samples\Linear array sample recordings\LinearArray-60-degrees\recording_2024-09-30_12-58-35_channel_6.wav")
    
    sources, rate = sf.read(path2source)
    #rate, signal1 = wavfile.read(filepath1)
    #rate, signal2 = wavfile.read(filepath2)
    #rate, signal3 = wavfile.read(filepath3)
    #rate, signal4 = wavfile.read(filepath4)
    #rate, signal5 = wavfile.read(filepath5)
    #rate, signal6 = wavfile.read(filepath6)
    print ("ayo")
    print (sources.shape)
    #print(signal1.shape)

    signal1 = sources[:,0]
    signal2 = sources[:,1]
    signal3 = sources[:,2]
    signal4 = sources[:,3]
    signal5 = sources[:,4]
    signal6 = sources[:,5]
    

    
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
    bin = 16
    X = Sx_all[:,bin , :]
    print(X.shape) 
    Rx = np.cov(X)
    
    M = 6
    d = 0.1
    v = 343
    f0 = f_bins[bin]
    theta_range = np.linspace(-90,90,1000)
    pspec = MVDR(theta_range, M, d, v, f0, Rx)
    print ("done with MVDR")
    print (bin * Delta_f)
    

    plt.figure(figsize=(7, 4))
    plt.plot(theta_range, pspec, linewidth=2)

    ymax = np.max(pspec)

    # vertical lines at the two source angles
    plt.axvline(61.9, linestyle='--', color='red')
    #plt.axvline(6,  linestyle='--', color='red')

    # labels for the lines, shifted so they don't overlap
    plt.text(61.9-7, ymax*0.9, "61.9°",
             ha='right', va='bottom', fontsize=12, color='red')
    #plt.text(6 + 3,  ymax*0.9, "6°",
             #ha='left',  va='bottom', fontsize=12, color='red')

    plt.xlabel("Angle (degrees)")
    plt.ylabel("Beamformer output")
    plt.title("Beamformer (1 source at 60°) / Bin Frequency = 1687 Hz")

    plt.grid(True, linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.show()




