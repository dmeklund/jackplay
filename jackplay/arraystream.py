"""
Support transparent streaming of data via backing arrays.
"""
from collections import deque

import numpy as np


class ArrayStream(object):
    """
    Store a processing stream of data backed by numpy arrays. Drops references to old data as new data is streamed in.
    """
    def __init__(self, maxlen):
        """
        Initialize an array stream with a fixed maximum number of backing arrays. Note that maxlen refers to the max
        number of backing arrays; we do not look at the size of the arrays themselves until we attempt to read data
        back out.
        :param maxlen: maximum number of backing arrays
        """
        self._maxlen = maxlen
        self._arrays = deque()

    def append(self, new_arr):
        """
        Append a new array of data to the stream. If we're at the maximum number of backing arrays, drop the oldest
        from the stream.
        :param new_arr: new array data to append
        :return:
        """
        self._arrays.append(new_arr.copy())
        while len(self._arrays) > self._maxlen:
            self._arrays.popleft()

    def get(self, data_len):
        """
        Retrieve a set number of most recent data points from the backing arrays. If there's not enough data to
        fill an array of length data_len, pad the beginning with zeros.
        :param data_len: number of elements to query and return
        :return: a zero-padded numpy array of length data_len
        """
        # we simply create an array of zeros of the specified length and then fill it in with data from the backing
        # arrays. no real attempt at optimization is made here.
        result_arr = np.zeros(data_len)
        offset = 0
        remaining_len = data_len
        for ind in range(len(self._arrays)-1, -1, -1):
            array = self._arrays[ind]
            array_len = len(array)
            if array_len <= remaining_len:
                result_arr[-array_len-offset:-offset or None] = array
                remaining_len -= array_len
                offset += array_len
            else:
                result_arr[-remaining_len-offset:-offset or None] = array[-remaining_len:]
                remaining_len = 0
            if remaining_len == 0:
                break
        return result_arr
