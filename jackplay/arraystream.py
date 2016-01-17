from collections import deque

import numpy as np


class ArrayStream(object):
    def __init__(self, maxlen):
        self._maxlen = maxlen
        self._arrays = deque()

    def append(self, new_arr):
        self._arrays.append(new_arr)
        while len(self._arrays) >= self._maxlen:
            self._arrays.popleft()

    def get(self):
        if len(self._arrays) == 0:
            return np.zeros(1)
        else:
            return np.concatenate(self._arrays)