from collections import deque

import numpy as np


class ArrayStream(object):
    def __init__(self, maxlen):
        self._maxlen = maxlen
        self._arrays = deque()

    def append(self, new_arr):
        self._arrays.append(new_arr.copy())
        while len(self._arrays) > self._maxlen:
            self._arrays.popleft()

    def get(self, data_len):
        # if len(self._arrays) > 5:
        #     import ipdb; ipdb.set_trace()
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
