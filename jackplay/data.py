"""
Data processing classes
"""
from .arraystream import ArrayStream


class SignalProcessor(object):
    """
    Thin layer on top of our backing stream that incorporates information we know about the signal we'll be processing
    to handle translation from time to data points.
    """
    def __init__(self, sample_rate, max_time_sec, block_size):
        self._sample_rate = sample_rate
        self._block_size = block_size
        self._max_time_sec = max_time_sec
        self._datastream = ArrayStream(int(sample_rate / block_size * max_time_sec))

    def register_data(self, data_arr):
        """
        Register a new set of incoming data with the stream.
        :param data_arr: new data array to append to the data stream
        """
        self._datastream.append(data_arr)

    def get_data(self, time_sec):
        """
        Retrieve the most recent data from the stream, up to the provided number of seconds.
        :param time_sec: seconds worth of data to return
        :return: zero-padded array of time_sec worth of data
        """
        return self._datastream.get(time_sec * self._sample_rate)
