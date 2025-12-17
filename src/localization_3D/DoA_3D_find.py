import numpy as np
from scipy.signal import ShortTimeFFT
from scipy.signal.windows import gaussian
from scipy.io import wavfile
from pathlib import Path
import matplotlib.pyplot as plt
import soundfile as sf
from loc import a_z
from loc import mvdr_z
from loc import music_z
from loc import generate_scan_points
from loc import generate_mic_positions




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
    bin = 9
    central_freq = bin*Delta_f
    X = Sx_all[:,bin , :]
    print(X.shape)
    print(central_freq)


    #Now we got the X selected

    #define parameters
    Q = 2
    M = 6
    v = 343
    f0 = central_freq
    d = 0.10
    Rx = (X @ X.conj().T) / X.shape[1]
    radius = 7
    zoff = 0.2
    xyz_points = generate_scan_points(radius, zoff)
    mic_positions = generate_mic_positions(d, M)

    Pout = mvdr_z(Rx, M, xyz_points, v, f0, mic_positions)
    print(xyz_points)
    print(Pout.shape)
    
    point_range = np.arange(len(Pout))
    plt.plot(point_range, Pout)

    
    plt.show()