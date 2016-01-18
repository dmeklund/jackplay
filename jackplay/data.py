from .arraystream import ArrayStream


class DataProcessor(object):
    def __init__(self, sample_rate, max_time_sec, block_size):
        self._sample_rate = sample_rate
        self._block_size = block_size
        self._max_time_sec = max_time_sec
        self._datastream = ArrayStream(int(sample_rate / block_size * max_time_sec))

    def register_data(self, data_arr):
        self._datastream.append(data_arr)

    def get_data(self, time_sec):
        return self._datastream.get(time_sec * self._sample_rate)
