import numpy as np
from scipy import signal


def remove_dc_offset(data):
    return data - data.mean()


def notch_filter(x, fs, notch_freq=50, quality_factor=20, ampl_response=False):

    b, a = signal.iirnotch(notch_freq, quality_factor, fs)
    filtered_x = signal.lfilter(b, a, x)
    if ampl_response:
        freq, h = signal.freqz(b, a, fs=fs)
        return filtered_x, freq, h
    return filtered_x
    

def butter_filter(x, fs, low_f, high_f, order=1, ampl_response=False):

    b, a = signal.butter(order, [low_f, high_f], btype='bandpass', fs=fs)
    filtered_x = signal.lfilter(b, a, x)
    if ampl_response:
        freq, h = signal.freqz(b, a, fs=fs)
        return filtered_x, freq, h
    return filtered_x


def filter(data, fs, bandpass = [6,30]):

    # removing DC offset
    noisy_data = np.apply_along_axis(remove_dc_offset, -1, data)
    # Notch filter
    quality_factor = 20
    notch_freq = 50.0
    data_notch = np.apply_along_axis(notch_filter, -1, noisy_data, fs, notch_freq, quality_factor)
    # Chebyshev bandpass filter
    low = bandpass[0]
    high = bandpass[1]
    order = 6
    data_filtered = np.apply_along_axis(butter_filter, -1, data_notch, fs, low, high, order)
    return data_filtered


def signal_fft(data, fs):

    n_fft = int(2**np.ceil(np.log2(data.shape[0])))
    data_fft = np.fft.fft(data, n = n_fft, axis = 0)
    data_fft = np.abs(data_fft)
    data_fft = data_fft[:len(data_fft)//2, :]
    data_fft[1:,] = 2*data_fft[1:,:]

    f = np.fft.fftfreq(n_fft, 1/fs)
    f = f[:len(f)//2]
    f = [round(x, 3) for x in f]
    return (data_fft, f)


