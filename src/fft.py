import sys
import json
from typing import NamedTuple

import matplotlib.pyplot as plt
import numpy as np
from scipy.fft import fft
from scipy.signal import find_peaks


class Peak(NamedTuple):
    freq: float
    intensity: float


def get_peaks(data, internals=None, limit=5000):
    data.sort(key=lambda x: x[0])
    time = np.array([t / 1e6 for t, _ in data])
    ampie = np.array([a for _, a in data])
    time -= np.min(time)
    intie = time[1:] - time[:-1]
    fourier = np.abs(fft(ampie))
    sampling_freq = 1/np.mean(intie)
    freq = np.arange(len(time)) * sampling_freq / len(time)
    peaks, _ = find_peaks(fourier, distance=30 * len(time)/sampling_freq)
    # peaks = peaks[peaks > 200 * len(time)/sampling_freq]
    peak_loc = [p for p in peaks if 50 < freq[p] < limit]
    peak_loc.sort(key=lambda i: fourier[i], reverse=True)

    if internals is not None:
        internals.update(locals()) # for debugging

    return [Peak(freq[i], fourier[i]) for i in peak_loc[:3]]

def main():
    with open([*sys.argv, "owo.json"][1], "r") as fin:
        ii = 3
        data = json.load(fin)[4096:4096*2]

    peaks = get_peaks(data, globals())

    for peak in peaks:
        print(peak)

    plt.plot(freq, np.abs(fourier))
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Intensity")
    plt.xlim([50, 2000])
    plt.ylim([0, fourier[peak_loc[0]] * 2])
    plt.show()

if __name__ == "__main__":
    main()
