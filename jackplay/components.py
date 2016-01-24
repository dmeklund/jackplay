"""
Signal processing and visualization components
"""
from scipy.signal import periodogram, spectrogram
import scipy.signal as signal
import numpy as np


class PeriodogramComponent(object):
    """
    Compute a real-time periodogram of the incoming signal.
    """
    def __init__(self, datastream, time_secs, sample_rate, max_freq=1500):
        self._datastream = datastream
        self._sample_rate = sample_rate
        self._time_secs = time_secs
        self._max_freq = max_freq

    def get_periodogram(self):
        data = self._datastream.get_data(self._time_secs)
        f, pxx = periodogram(data, self._sample_rate)
        return pxx[f<=self._max_freq]


class SpectrogramComponent(object):
    """
    Compute a real-time spectrogram of the incoming signal.
    """
    def __init__(self, datastream, time_secs, sample_rate, max_freq=1500):
        self._datastream = datastream
        self._sample_rate = sample_rate
        self._time_secs = time_secs
        self._max_freq = max_freq

    def get_spectrogram(self):
        data = self._datastream.get_data(self._time_secs)
        f, t, sxx = spectrogram(data, self._sample_rate, nperseg=8192, noverlap=1024)
        # transpose the data so that it will display time on the X-axis and frequency on the Y-axis
        return sxx[f<=self._max_freq,:].T


class LowPassFilter(object):
    """
    Apply a low-pass filter to the incoming signal.
    """
    def __init__(self, processor, max_freq, sample_rate):
        self._proc = processor
        self._max_freq = max_freq
        self._sample_rate = sample_rate

    def filter(self, chunk):
        chunk = self._proc.get_data(0.2)
        b, a = signal.butter(5, self._max_freq / (self._sample_rate / 2), btype='low', analog=False)
        out = signal.lfilter(b, a, chunk).astype(np.float32)
        return out[-1024:]


class VariableBandPassFilter(object):
    """
    Use the most prominent frequency of a modulation input signal to apply a bandpass filter to the input signal.
    """
    def __init__(self, proc_input, proc_modulate, sample_rate):
        self._proc_input = proc_input
        self._proc_modulate = proc_modulate
        self._sample_rate = sample_rate

    def filter(self):
        chunk = self._proc_input.get_data(0.2)
        modulate = self._proc_modulate.get_data(1.0)
        f, pxx = periodogram(modulate, self._sample_rate)
        # go up an octave (2x frequency)
        desired = 2 * f[pxx.argmax()] / (self._sample_rate / 2)
        # print('desired frequency:', desired)
        b, a = signal.butter(5, [.8 * desired, 1.4*desired], btype='band', analog=False)
        out = signal.lfilter(b, a, chunk).astype(np.float32)
        return out[-1024:]
