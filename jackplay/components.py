from scipy.signal import periodogram, spectrogram
import scipy.signal as signal
import numpy as np
import random
import time

starttime = time.time()

class PeriodogramComponent(object):
    def __init__(self, datastream, time_secs, sample_rate):
        self._datastream = datastream
        self._sample_rate = sample_rate
        self._time_secs = time_secs

    def get_periodogram(self):
        # import ipdb; ipdb.set_trace()
        data = self._datastream.get_data(self._time_secs)
        f, pxx = periodogram(data, self._sample_rate)
        # import ipdb; ipdb.set_trace()
        return pxx[f<1500]


class SpectrogramComponent(object):
    def __init__(self, datastream, time_secs, sample_rate):
        self._datastream = datastream
        self._sample_rate = sample_rate
        self._time_secs = time_secs

    def get_spectrogram(self):
        data = self._datastream.get_data(self._time_secs)
        f, t, sxx = spectrogram(data, self._sample_rate, nperseg=8192, noverlap=1024)
        # if time.time() > starttime + 15:
        #     import ipdb; ipdb.set_trace()
        # if random.random() < .05:
        #     import ipdb; ipdb.set_trace()
        return sxx[f<1500,:].T


class LowPassFilter(object):
    def __init__(self, processor, max_freq, sample_rate):
        self._proc = processor
        self._max_freq = max_freq
        self._sample_rate = sample_rate

    def filter(self, chunk):
        # import ipdb; ipdb.set_trace()
        chunk = self._proc.get_data(0.2)
        b, a = signal.butter(5, self._max_freq / (self._sample_rate / 2), btype='low', analog=False)
        out = signal.lfilter(b, a, chunk).astype(np.float32)
        return out[-1024:]


class VariableBandPassFilter(object):
    def __init__(self, proc_input, proc_modulate, sample_rate):
        self._proc_input = proc_input
        self._proc_modulate = proc_modulate
        self._sample_rate = sample_rate

    def filter(self):
        chunk = self._proc_input.get_data(0.2)
        modulate = self._proc_modulate.get_data(1.0)
        f, pxx = periodogram(modulate, self._sample_rate)
        # go up an octave (2*)
        desired = 2 * f[pxx.argmax()] / (self._sample_rate / 2)
        # desired = 0.05
        print('desired frequency:', desired)
        try:
            b, a = signal.butter(5, [.8 * desired, 1.4*desired], btype='band', analog=False)
        except ValueError:
            import ipdb; ipdb.set_trace()
        out = signal.lfilter(b, a, chunk).astype(np.float32)
        return out[-1024:]
