"""
The JackPlay jack client
"""
from .plotter import QtPlotter
from .arraystream import ArrayStream

import jack
import numpy as np

import threading
import time


class JackPlay(object):
    def __init__(self, client_name):
        # self._fig = None
        self._ax = None
        self._line = None
        self._lastupdate = time.time()
        self._client = jack.Client(client_name)
        self._event = threading.Event()
        self._plotter = QtPlotter()
        self._data = ArrayStream(5)
        # self._lastdata = np.zeros(1024)
        self._initialize()

    def _process(self, frames):
        for inport, outport in zip(self._client.inports, self._client.outports):
            self._data.append(inport.get_array())
            # self._lastdata = inport.get_array()
            outport.get_buffer()[:] = inport.get_buffer()

    def _shutdown(self, status, reason):
        print("JACK shutdown!")
        print("status:", status)
        print("reason:", reason)
        self._event.set()

    def _initialize(self):
        self._client.set_process_callback(self._process)
        self._client.set_shutdown_callback(self._shutdown)
        # for number in 1,: #, 2:
        self._client.inports.register("input_1") #.format(number))
        self._client.outports.register("output_1") #.format(number))
        self._plotter.add_plot("raw", "Raw Data", self._data.get)

    def run(self):
        with self._client:
            capture = self._client.get_ports(is_physical=True, is_output=True)
            for src, dest in zip(capture, self._client.inports):
                self._client.connect(src, dest)
            playback = self._client.get_ports(is_physical=True, is_input=True)
            for src, dest in zip(self._client.outports, playback):
                self._client.connect(src, dest)
            self._plotter.run()
            # print("Press Ctrl-C to stop")
            # try:
            #     self._event.wait()
            # except KeyboardInterrupt:
            #     print("\nInterrupted by user")


def main():
    JackPlay("jackplay").run()


if __name__ == "__main__":
    main()
