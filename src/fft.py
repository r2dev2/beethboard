import json

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft, fftfreq

with open("owo.json", "r") as fin:
    data = json.load(fin)

data.sort(key=lambda x: x[0])
time = np.array([t / 1e6 for t, _ in data])
ampie = np.array([a for _, a in data])
time -= np.min(time)

interval = np.where(time < 2.5)
# interval = slice(256 * 3, 256 * 4)
time = time[interval]
ampie = ampie[interval]

intie = time[1:] - time[:-1]
print(np.mean(intie), np.std(intie))
print(max(intie), min(intie))

fourier = fft(ampie)

# sampling_freq = len(time) / (np.max(time) - np.min(time))
sampling_freq = 1/np.mean(intie)
freq = np.arange(len(time)) * sampling_freq / len(time)
plt.plot(freq, np.abs(fourier))
plt.xlabel("Frequency (Hz)")
plt.ylabel("Intensity")
plt.xlim([50, 1500])
plt.ylim([0, 1e5])
plt.show()

exit()

# print(time[32::32] - time[:-32:32])

# plt.plot(time, ampie)
# plt.show()

# sampling_freq = 32 / (time[-32] - time[0])
sampling_freq = len(time) / (np.max(time) - np.min(time))
print(sampling_freq)
# sampling_freq = 5e3
plt.specgram(ampie, Fs=sampling_freq, NFFT=250)
plt.show()
