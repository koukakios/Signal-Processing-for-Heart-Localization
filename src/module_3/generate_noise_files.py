from scipy.io.wavfile import write
import winsound
import wave 
import os

Fs = 48000
#signal1 = np.random.randint(-5000, 5000, Fs).astype(np.int16)
#signal2 = np.random.randint(-5000, 5000, Fs).astype(np.int16)
#signal3 = np.random.randint(-5000, 5000, Fs).astype(np.int16)
#write("file1.wav", Fs, signal1)
#write("file2.wav", Fs, signal3)
#write("file3.wav", Fs, signal2)

file_path = os.path.abspath("file1.wav")
print(f"Trying to play: {file_path}")
winsound.PlaySound(file_path, winsound.SND_FILENAME)
winsound.PlaySound("file2.wav", winsound.SND_FILENAME)
winsound.PlaySound("file3.wav", winsound.SND_FILENAME)
